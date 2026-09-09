"""Client Open-Meteo Previous Runs / Open-Meteo Previous Runs client.

FR : L'API Previous Runs renvoie, pour chaque heure de validité, la valeur
prévue par le run émis N jours plus tôt (variable suffixée
`_previous_dayN`, N = 1..7). C'est une archive de prévisions à lead fixe,
donc un backtest strict point-in-time sans stocker soi-même les runs.
Ce client est la version « production » de la logique jusque-là confinée
dans scripts/_backfill_dataset.py : requêtes par plage de dates (pas jour
par jour), fuseau GMT pour permettre l'agrégation en heure standard
locale (voir src/truth/lst_window.py), cache disque partagé.

EN : The Previous Runs API returns, for each valid hour, the value
forecast by the run issued N days earlier (`_previous_dayN` suffix,
N = 1..7). A fixed-lead forecast archive, hence a strict point-in-time
backtest without hosting runs ourselves. Production version of the logic
previously confined to scripts/_backfill_dataset.py: date-range requests,
GMT timezone so aggregation can use local standard time, shared disk cache.

Observed limits (2026-06, backfill summary): the free tier serves about
the last 60 days for the AI models; GFS goes back further. Coverage is
measured, never assumed: see `coverage()`.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import requests

from src.config import DATA_DIR
from src.weather.open_meteo import AVAILABLE_MODELS, DEFAULT_ENSEMBLE, OpenMeteoClient

PREVIOUS_RUNS_BASE = "https://previous-runs-api.open-meteo.com/v1/forecast"
PREV_RUNS_CACHE_DIR = DATA_DIR / "backfill_cache"
MAX_DAYS_PER_REQUEST = 31
POLITE_SLEEP_S = 0.2


@dataclass
class HourlyLeadSeries:
    """Série horaire UTC d'un modèle à un lead donné."""
    model: str
    lead_days: int
    times_utc: list[str] = field(default_factory=list)
    values: list[Optional[float]] = field(default_factory=list)

    @property
    def n_valid(self) -> int:
        return sum(1 for v in self.values if v is not None)


class PreviousRunsClient:
    def __init__(self, cache_dir: Path = PREV_RUNS_CACHE_DIR,
                 models: Optional[list[str]] = None,
                 leads: Optional[list[int]] = None,
                 sleep_s: float = POLITE_SLEEP_S):
        self.models = list(models or DEFAULT_ENSEMBLE)
        unknown = [m for m in self.models if m not in AVAILABLE_MODELS]
        if unknown:
            raise ValueError(f"Modèles inconnus : {unknown}")
        self.leads = sorted(set(leads or [1, 2, 3, 4, 5, 6, 7]))
        if any(n < 1 or n > 7 for n in self.leads):
            raise ValueError("leads must be within 1..7 (Previous Runs limit)")
        self.sleep_s = sleep_s
        # Réutilise le transport (retry, 429, cache sécurisé) du client existant.
        self._om = OpenMeteoClient(cache_dir=cache_dir)

    # -- requêtes --

    def _params(self, lat: float, lon: float, start: date, end: date,
                variable: str) -> dict:
        hourly = [f"{variable}_previous_day{n}" for n in self.leads]
        return {
            "latitude": lat, "longitude": lon,
            "start_date": start.isoformat(), "end_date": end.isoformat(),
            "hourly": ",".join(hourly),
            "models": ",".join(self.models),
            "timezone": "GMT",
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "mm",
        }

    def _fetch_chunk(self, lat: float, lon: float, start: date, end: date,
                     variable: str) -> dict:
        key = (f"{lat:.4f}_{lon:.4f}_{start.isoformat()}_{end.isoformat()}"
               f"_{variable}_l{'-'.join(map(str, self.leads))}"
               f"_{'-'.join(sorted(self.models))}")

        def fetcher() -> dict:
            time.sleep(self.sleep_s)
            return self._om._get(PREVIOUS_RUNS_BASE, self._params(lat, lon, start, end, variable))

        return self._om.cached_or_fetch("prevruns_range", key, fetcher)

    def fetch(self, lat: float, lon: float, start: date, end: date,
              variable: str = "temperature_2m") -> dict[str, dict[int, HourlyLeadSeries]]:
        """{model: {lead: HourlyLeadSeries}} sur [start, end], en UTC.

        Les plages longues sont découpées en morceaux de MAX_DAYS_PER_REQUEST.
        Un morceau qui échoue (400/500, plage hors archive) est journalisé
        dans `self.failed_chunks` et sauté : la couverture réelle se lit
        ensuite via coverage().
        """
        out: dict[str, dict[int, HourlyLeadSeries]] = {
            m: {n: HourlyLeadSeries(m, n) for n in self.leads} for m in self.models
        }
        self.failed_chunks: list[tuple[date, date, str]] = getattr(self, "failed_chunks", [])
        cur = start
        while cur <= end:
            chunk_end = min(end, cur + timedelta(days=MAX_DAYS_PER_REQUEST - 1))
            try:
                data = self._fetch_chunk(lat, lon, cur, chunk_end, variable)
            except requests.RequestException as e:
                self.failed_chunks.append((cur, chunk_end, str(e)))
                cur = chunk_end + timedelta(days=1)
                continue
            self._merge(data, variable, out)
            cur = chunk_end + timedelta(days=1)
        return out

    def _merge(self, data: dict, variable: str,
               out: dict[str, dict[int, HourlyLeadSeries]]) -> None:
        hourly = (data or {}).get("hourly") or {}
        times = hourly.get("time") or []
        for m in self.models:
            for n in self.leads:
                k = f"{variable}_previous_day{n}_{m}"
                if k not in hourly and len(self.models) == 1:
                    k = f"{variable}_previous_day{n}"       # réponse mono-modèle
                vals = hourly.get(k)
                if vals is None:
                    continue
                s = out[m][n]
                s.times_utc.extend(times)
                s.values.extend(vals)

    # -- diagnostic --

    @staticmethod
    def coverage(series: dict[str, dict[int, HourlyLeadSeries]]) -> dict[str, dict[int, dict]]:
        """Premier/dernier jour avec données et nombre d'heures valides, par modèle et lead."""
        cov: dict[str, dict[int, dict]] = {}
        for m, by_lead in series.items():
            cov[m] = {}
            for n, s in by_lead.items():
                days = sorted({t[:10] for t, v in zip(s.times_utc, s.values) if v is not None})
                cov[m][n] = {
                    "first_day": days[0] if days else None,
                    "last_day": days[-1] if days else None,
                    "n_days": len(days),
                    "n_hours_valid": s.n_valid,
                }
        return cov
