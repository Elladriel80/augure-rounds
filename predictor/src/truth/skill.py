"""Backtest de skill station, sans marché / Market-free station skill backtest.

FR : Trois politiques de conversion prévision → P(bin), toutes scorées
contre la vérité CLI sur des bins synthétiques Kalshi :

  raw          mu = moyenne des modèles, sigma = dispersion inter-modèles
               (plancher 1 °F). C'est la politique B en production depuis
               le 2026-06-20 (PR #160), reproduite ici hors marché.
  station_bias mu = moyenne des modèles + biais station appris sur TRAIN,
               sigma = écart-type des résidus sur TRAIN, par (station,
               variable, lead). EMOS minimal, deux paramètres, lisibles.
  climatology  N(moyenne, écart-type) des observations CLI des années
               précédentes sur une fenêtre ±window_days autour du jour de
               l'année. Baseline honnête, calculée sur la VRAIE station et
               non sur ERA5.

Le split est temporel par date cible : TRAIN = dates < split_date,
HOLDOUT = dates ≥ split_date. Le biais station n'est estimé que sur TRAIN.

EN : Three forecast → P(bin) policies, all scored against CLI truth on
Kalshi-shaped synthetic bins: raw (model mean, inter-model sigma floored
at 1 °F: the production policy since PR #160), station_bias (mean + bias
learned on TRAIN, residual sigma on TRAIN, per station/variable/lead:
minimal two-parameter EMOS), climatology (CLI-based N(mean, sd) over a
day-of-year window of previous years). Temporal split by target date.
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

from .iem_cli import CliDay
from .lst_window import daily_extreme_lst
from .synthetic_bins import Bin, brier, kalshi_style_bins, prob_in_bin_gaussian
from src.weather.previous_runs import HourlyLeadSeries

SIGMA_FLOOR_F = 1.0
MIN_TRAIN_PAIRS = 20
MIN_CLIMO_OBS = 15


@dataclass(frozen=True)
class ForecastPoint:
    """Prévision agrégée d'un jour cible à un lead donné."""
    station: str
    variable: str            # temp_max | temp_min
    target: date
    lead: int
    per_model: dict          # {model: valeur °F}

    @property
    def mean(self) -> float:
        return statistics.fmean(self.per_model.values())

    @property
    def spread(self) -> float:
        vals = list(self.per_model.values())
        return statistics.pstdev(vals) if len(vals) >= 2 else 0.0


def build_forecast_points(
    station: str,
    variable: str,
    tz_name: str,
    series: dict[str, dict[int, HourlyLeadSeries]],
    targets: list[date],
    min_models: int = 2,
) -> list[ForecastPoint]:
    """Agrège les séries horaires Previous Runs en extrêmes journaliers LST."""
    kind = "max" if variable == "temp_max" else "min"
    out: list[ForecastPoint] = []
    for t in targets:
        for lead in sorted({n for by_lead in series.values() for n in by_lead}):
            per_model: dict[str, float] = {}
            for model, by_lead in series.items():
                s = by_lead.get(lead)
                if s is None or not s.times_utc:
                    continue
                v = daily_extreme_lst(s.times_utc, s.values, tz_name, t, kind)
                if v is not None:
                    per_model[model] = v
            if len(per_model) >= min_models:
                out.append(ForecastPoint(station, variable, t, lead, per_model))
    return out


# --------------------------------------------------------------- climatology

def climatology_gaussian(
    truth: list[CliDay], variable: str, target: date,
    window_days: int = 7, years_back: int = 8,
) -> Optional[tuple[float, float]]:
    """(mu, sigma) des observations CLI des `years_back` années précédentes,
    jours à ±window_days du jour de l'année de `target`. Strict point-in-time :
    n'utilise que les années < target.year."""
    vals: list[float] = []
    by_date = {d.valid: d for d in truth}
    for y in range(target.year - years_back, target.year):
        try:
            anchor = target.replace(year=y)
        except ValueError:           # 29 février
            anchor = date(y, 2, 28)
        for k in range(-window_days, window_days + 1):
            d = by_date.get(anchor + timedelta(days=k))
            if d is None:
                continue
            v = d.value_for(variable)
            if v is not None:
                vals.append(v)
    if len(vals) < MIN_CLIMO_OBS:
        return None
    return statistics.fmean(vals), max(SIGMA_FLOOR_F, statistics.pstdev(vals))


# -------------------------------------------------------------- station bias

@dataclass
class StationBias:
    """Biais et sigma résiduel par (station, variable, lead), appris sur TRAIN."""
    params: dict = field(default_factory=dict)   # (station, var, lead) → (bias, sigma, n)

    def fit(self, points: list[ForecastPoint], truth_by: dict[tuple[str, date], CliDay]) -> "StationBias":
        resid: dict[tuple, list[float]] = defaultdict(list)
        for p in points:
            d = truth_by.get((p.station, p.target))
            if d is None:
                continue
            obs = d.value_for(p.variable)
            if obs is None:
                continue
            resid[(p.station, p.variable, p.lead)].append(obs - p.mean)
        for k, r in resid.items():
            if len(r) >= MIN_TRAIN_PAIRS:
                b = statistics.fmean(r)
                s = statistics.pstdev(r) if len(r) > 1 else SIGMA_FLOOR_F
                self.params[k] = (b, max(SIGMA_FLOOR_F, s), len(r))
        return self

    def apply(self, p: ForecastPoint) -> Optional[tuple[float, float]]:
        k = (p.station, p.variable, p.lead)
        if k not in self.params:
            return None
        b, s, _ = self.params[k]
        return p.mean + b, s


# -------------------------------------------------------------------- scoring

@dataclass
class BinScore:
    station: str
    variable: str
    target: date
    lead: int
    bin_label: str
    outcome: bool
    p_raw: float
    p_station: Optional[float]
    p_climo: Optional[float]
    p_market: Optional[float] = None   # rempli plus tard si un marché existe


def score_points(
    points: list[ForecastPoint],
    truth_by: dict[tuple[str, date], CliDay],
    truth_lists: dict[str, list[CliDay]],
    bias: StationBias,
    n_central: int = 6,
) -> list[BinScore]:
    scores: list[BinScore] = []
    for p in points:
        d = truth_by.get((p.station, p.target))
        if d is None:
            continue
        obs = d.value_for(p.variable)
        if obs is None:
            continue
        mu_raw, sig_raw = p.mean, max(SIGMA_FLOOR_F, p.spread)
        st = bias.apply(p)
        cl = climatology_gaussian(truth_lists.get(p.station, []), p.variable, p.target)
        for b in kalshi_style_bins(mu_raw, n_central=n_central):
            if not b.is_central:
                continue
            scores.append(BinScore(
                station=p.station, variable=p.variable, target=p.target, lead=p.lead,
                bin_label=b.label(), outcome=b.contains(obs),
                p_raw=prob_in_bin_gaussian(mu_raw, sig_raw, b),
                p_station=prob_in_bin_gaussian(st[0], st[1], b) if st else None,
                p_climo=prob_in_bin_gaussian(cl[0], cl[1], b) if cl else None,
            ))
    return scores


def summarize(scores: list[BinScore], key) -> dict:
    """Brier moyen par politique, groupé par `key(score)`. Ne compare que
    les lignes où toutes les politiques présentes sont définies."""
    groups: dict = defaultdict(list)
    for s in scores:
        groups[key(s)].append(s)
    out: dict = {}
    for g, rows in sorted(groups.items(), key=lambda kv: str(kv[0])):
        common = [r for r in rows if r.p_station is not None and r.p_climo is not None]
        if not common:
            continue
        out[g] = {
            "n_bins": len(common),
            "n_dates": len({r.target for r in common}),
            "base_rate": statistics.fmean(1.0 if r.outcome else 0.0 for r in common),
            "brier_raw": statistics.fmean(brier(r.p_raw, r.outcome) for r in common),
            "brier_station": statistics.fmean(brier(r.p_station, r.outcome) for r in common),
            "brier_climo": statistics.fmean(brier(r.p_climo, r.outcome) for r in common),
        }
        if any(r.p_market is not None for r in common):
            mk = [r for r in common if r.p_market is not None]
            out[g]["n_bins_market"] = len(mk)
            out[g]["brier_market"] = statistics.fmean(brier(r.p_market, r.outcome) for r in mk)
            out[g]["brier_station_on_market_rows"] = statistics.fmean(
                brier(r.p_station, r.outcome) for r in mk)
    return out


def sign_test_by_date(scores: list[BinScore], a: str, b: str) -> dict:
    """Sign test exact : sur combien de dates distinctes la politique `a`
    a-t-elle un Brier moyen strictement inférieur à `b` ? p-value binomiale
    unilatérale (H0 : 50 %). Comparaison par date, jamais par ligne : les
    bins d'une même journée voient la même météo."""
    by_date: dict[date, list[BinScore]] = defaultdict(list)
    for s in scores:
        if getattr(s, a) is not None and getattr(s, b) is not None:
            by_date[s.target].append(s)
    wins = losses = 0
    for rows in by_date.values():
        ba = statistics.fmean(brier(getattr(r, a), r.outcome) for r in rows)
        bb = statistics.fmean(brier(getattr(r, b), r.outcome) for r in rows)
        if ba < bb:
            wins += 1
        elif ba > bb:
            losses += 1
    n = wins + losses
    p = _binom_sf(wins, n) if n else None
    return {"a": a, "b": b, "dates": n, "a_wins": wins, "p_one_sided": p}


def _binom_sf(k: int, n: int) -> float:
    """P(X ≥ k) pour X ~ Bin(n, 0.5)."""
    return sum(math.comb(n, i) for i in range(k, n + 1)) / (2 ** n)
