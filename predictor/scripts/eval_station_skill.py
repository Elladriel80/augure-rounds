"""eval_station_skill.py — skill des prévisions contre la vérité CLI, sans marché.

FR : Pour chaque station et variable (temp_max, temp_min), agrège les
prévisions Previous Runs (leads 1..7) en extrêmes journaliers dans la
fenêtre LST du CLI, fabrique des bins synthétiques Kalshi autour de la
moyenne des modèles, et score trois politiques contre la vérité CLI :
`raw` (politique de production), `station_bias` (biais + sigma appris sur
TRAIN, par station/variable/lead) et `climatology` (CLI, années précédentes).
Split temporel par date cible ; le HOLDOUT n'est lu qu'une fois.

Ce backtest ne dépend pas de l'existence d'un marché Kalshi : il mesure le
skill de la chaîne prévision → P(bin) sur toute la profondeur d'archive
disponible, et fournit les paramètres de correction station (A1/B1 de la
note du 2026-09-09) prêts à être injectés dans le predictor.

EN : Per station and variable, aggregates Previous Runs forecasts (leads
1..7) to daily extremes in the CLI LST window, builds Kalshi-shaped bins
around the model mean and scores three policies against CLI truth: raw
(production policy), station_bias (bias + sigma learned on TRAIN per
station/variable/lead) and climatology (CLI, previous years). Temporal
split by target date; HOLDOUT read once. Market-independent.

Réseau requis / Network required (IEM + Open-Meteo Previous Runs).

Usage:
    python scripts/eval_station_skill.py                       # 18 stations, 120 derniers jours
    python scripts/eval_station_skill.py --stations KNYC,KSFO --start 2026-04-01
    python scripts/eval_station_skill.py --leads 1,2,3 --split-frac 0.7
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.truth.iem_cli import TRUTH_DIR, IEMCliClient, kalshi_stations  # noqa: E402
from src.truth.skill import (  # noqa: E402
    BinScore, ForecastPoint, StationBias, build_forecast_points, score_points,
    sign_test_by_date, summarize,
)
from src.weather.open_meteo import DEFAULT_ENSEMBLE  # noqa: E402
from src.weather.previous_runs import PreviousRunsClient  # noqa: E402

CLIMO_YEARS_BACK = 8


def fmt_table(title: str, summ: dict, key_name: str) -> list[str]:
    lines = [f"### {title}", "",
             f"| {key_name} | n bins | n dates | base rate | Brier raw | Brier station_bias | Brier climato | Δ station − raw |",
             "|---|---|---|---|---|---|---|---|"]
    for k, r in summ.items():
        lines.append(
            f"| {k} | {r['n_bins']} | {r['n_dates']} | {r['base_rate']:.3f} | {r['brier_raw']:.4f} "
            f"| {r['brier_station']:.4f} | {r['brier_climo']:.4f} | {r['brier_station'] - r['brier_raw']:+.4f} |"
        )
    return lines + [""]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stations", default="")
    ap.add_argument("--variables", default="temp_max,temp_min")
    ap.add_argument("--start", default=(date.today() - timedelta(days=120)).isoformat())
    ap.add_argument("--end", default=(date.today() - timedelta(days=2)).isoformat(),
                    help="dernier jour cible (défaut : avant-hier, CLI final publié)")
    ap.add_argument("--leads", default="1,2,3,4,5,6,7")
    ap.add_argument("--models", default=",".join(DEFAULT_ENSEMBLE))
    ap.add_argument("--split-date", default="", help="début du HOLDOUT (défaut : --split-frac)")
    ap.add_argument("--split-frac", type=float, default=0.7, help="part TRAIN des dates distinctes")
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "skill"))
    args = ap.parse_args()

    stations = kalshi_stations()
    wanted = [s.strip().upper() for s in args.stations.split(",") if s.strip()] or list(stations)
    variables = [v.strip() for v in args.variables.split(",") if v.strip()]
    leads = [int(x) for x in args.leads.split(",")]
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    targets = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cli = IEMCliClient(cache_dir=TRUTH_DIR / "iem_cache")
    prev = PreviousRunsClient(models=models, leads=leads)

    points: list[ForecastPoint] = []
    truth_lists: dict = {}
    truth_by: dict = {}
    coverage: dict = {}
    for icao in wanted:
        meta = stations[icao]
        print(f"[{icao}] vérité CLI + previous runs {start} → {end} ...", flush=True)
        try:
            truth = cli.fetch_range(icao, date(start.year - CLIMO_YEARS_BACK, 1, 1), end)
        except Exception as e:  # noqa: BLE001
            print(f"   IEM échec : {e}")
            continue
        truth_lists[icao] = truth
        for d in truth:
            truth_by[(icao, d.valid)] = d
        series = prev.fetch(meta["lat"], meta["lon"], start, end, "temperature_2m")
        coverage[icao] = prev.coverage(series)
        for var in variables:
            pts = build_forecast_points(icao, var, meta["tz"], series, targets)
            points.extend(pts)
            print(f"   {var}: {len(pts)} points prévision")

    if not points:
        print("Aucun point : vérifie le réseau et la couverture Previous Runs.")
        return 1

    dates = sorted({p.target for p in points})
    if args.split_date:
        split = date.fromisoformat(args.split_date)
    else:
        split = dates[min(len(dates) - 1, int(len(dates) * args.split_frac))]
    train = [p for p in points if p.target < split]
    hold = [p for p in points if p.target >= split]
    print(f"\nSplit temporel : TRAIN < {split} ({len({p.target for p in train})} dates), "
          f"HOLDOUT ≥ {split} ({len({p.target for p in hold})} dates)")

    bias = StationBias().fit(train, truth_by)
    scores: list[BinScore] = score_points(hold, truth_by, truth_lists, bias)

    by_lead = summarize(scores, lambda s: s.lead)
    by_station = summarize(scores, lambda s: f"{s.station}/{s.variable}")
    by_var = summarize(scores, lambda s: s.variable)
    overall = summarize(scores, lambda s: "all")
    tests = {
        "station_vs_raw": sign_test_by_date(scores, "p_station", "p_raw"),
        "raw_vs_climo": sign_test_by_date(scores, "p_raw", "p_climo"),
        "station_vs_climo": sign_test_by_date(scores, "p_station", "p_climo"),
    }

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Skill station vs vérité CLI / Station skill vs CLI truth",
        "",
        f"Généré / generated : {now}. Cibles / targets : {start} → {end}. "
        f"Leads : {leads}. Modèles / models : {', '.join(models)}.",
        f"Split : TRAIN < {split}, HOLDOUT ≥ {split}. Bins synthétiques 2 °F centrés sur la moyenne des modèles ; "
        "seuls les bins centraux sont scorés (même filtre que le live).",
        "",
        "FR : `raw` = politique de production (moyenne des modèles, sigma inter-modèles, plancher 1 °F). "
        "`station_bias` = même moyenne + biais station appris sur TRAIN, sigma résiduel TRAIN. "
        "`climato` = observations CLI des années précédentes (±7 jours). Le HOLDOUT est lu une seule fois.",
        "EN : `raw` = production policy. `station_bias` = model mean + TRAIN-learned station bias, TRAIN residual sigma. "
        "`climato` = CLI observations of previous years (±7 days). HOLDOUT read once.",
        "",
    ]
    lines += fmt_table("Global / overall (HOLDOUT)", overall, "groupe")
    lines += fmt_table("Par lead / by lead (HOLDOUT)", by_lead, "lead (jours)")
    lines += fmt_table("Par variable / by variable (HOLDOUT)", by_var, "variable")
    lines += fmt_table("Par station / by station (HOLDOUT)", by_station, "station/variable")
    lines += ["### Sign tests par date / by date (HOLDOUT)", "",
              "| comparaison | dates | victoires a | p unilatéral |", "|---|---|---|---|"]
    for name, t in tests.items():
        p = f"{t['p_one_sided']:.4f}" if t["p_one_sided"] is not None else "n/a"
        lines.append(f"| {name} ({t['a']} < {t['b']}) | {t['dates']} | {t['a_wins']} | {p} |")
    lines += ["", "### Biais station appris sur TRAIN / TRAIN-learned station bias", "",
              "| station | variable | lead | biais obs − modèle (°F) | sigma résiduel (°F) | n |", "|---|---|---|---|---|---|"]
    for (st, var, lead), (b, s, n) in sorted(bias.params.items()):
        lines.append(f"| {st} | {var} | {lead} | {b:+.2f} | {s:.2f} | {n} |")
    lines += ["", "### Couverture Previous Runs / coverage", "",
              "| station | modèle | lead | premier jour | dernier jour | n jours |", "|---|---|---|---|---|---|"]
    for icao, per_model in sorted(coverage.items()):
        for m, per_lead in per_model.items():
            for n, c in per_lead.items():
                lines.append(f"| {icao} | {m} | {n} | {c['first_day']} | {c['last_day']} | {c['n_days']} |")
    if prev.failed_chunks:
        lines += ["", f"Morceaux Previous Runs en échec / failed chunks : {len(prev.failed_chunks)} "
                  "(voir skill_run.json)."]

    (out_dir / "skill_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Mémoire durable des prévisions agrégées : Previous Runs ne garde que
    # ~60 jours, ce fichier (fusionné à chaque run) est ce qui reste.
    fp_path = out_dir / "forecast_points.json"
    existing: dict[str, dict] = {}
    if fp_path.exists():
        try:
            for r in json.loads(fp_path.read_text(encoding="utf-8")):
                existing[f"{r['station']}|{r['variable']}|{r['target']}|{r['lead']}"] = r
        except (json.JSONDecodeError, KeyError, TypeError):
            existing = {}
    for p in points:
        existing[f"{p.station}|{p.variable}|{p.target.isoformat()}|{p.lead}"] = {
            "station": p.station, "variable": p.variable, "target": p.target.isoformat(),
            "lead": p.lead, "per_model": {m: round(v, 2) for m, v in p.per_model.items()}}
    fp_path.write_text(json.dumps(sorted(existing.values(), key=lambda r: (r["station"], r["variable"], r["target"], r["lead"])),
                                  separators=(",", ":")), encoding="utf-8")
    print(f"Mémoire prévisions : {fp_path} ({len(existing)} points cumulés)")

    (out_dir / "skill_scores.json").write_text(json.dumps(
        [{**asdict(s), "target": s.target.isoformat()} for s in scores], separators=(",", ":")),
        encoding="utf-8")
    (out_dir / "station_bias.json").write_text(json.dumps(
        [{"station": k[0], "variable": k[1], "lead": k[2], "bias_f": v[0], "sigma_f": v[1], "n_train": v[2]}
         for k, v in sorted(bias.params.items())], indent=2), encoding="utf-8")
    (out_dir / "skill_run.json").write_text(json.dumps({
        "schema": "station_skill_run/1", "generated_at": now,
        "params": {"stations": wanted, "variables": variables, "leads": leads, "models": models,
                   "start": start.isoformat(), "end": end.isoformat(), "split": split.isoformat()},
        "n_points_train": len(train), "n_points_holdout": len(hold), "n_bins_scored": len(scores),
        "overall": overall, "by_lead": by_lead, "by_variable": by_var, "by_station": by_station,
        "sign_tests": tests, "coverage": coverage,
        "failed_chunks": [[a.isoformat(), b.isoformat(), e] for a, b, e in prev.failed_chunks],
    }, indent=2), encoding="utf-8")

    print("\n".join(lines[:40]))
    print(f"\nRapport : {out_dir / 'skill_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
