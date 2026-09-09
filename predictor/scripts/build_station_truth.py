"""build_station_truth.py — vérité CLI par station + audit ERA5 vs CLI.

FR : Télécharge (avec cache) les rapports climatologiques quotidiens du NWS
pour les 18 stations de résolution Kalshi via l'archive IEM, écrit un
fichier compact `data/truth/cli_daily.json`, puis mesure l'écart entre la
« vérité » ERA5 utilisée jusqu'ici par la climatologie (Open-Meteo archive)
et la vérité CLI réelle : biais, MAE, part de jours exacts, par station et
par mois. C'est le chiffrage du défaut 1.2 de la note du 2026-09-09.

EN : Downloads (cached) the NWS Daily Climate Reports for the 18 Kalshi
resolution stations from the IEM archive, writes a compact
`data/truth/cli_daily.json`, then measures the gap between the ERA5
"truth" used so far by the climatology (Open-Meteo archive) and the real
CLI truth: bias, MAE, exact-day share, per station and month.

Réseau requis / Network required (IEM + Open-Meteo archive).

Usage:
    python scripts/build_station_truth.py                  # 2018 → hier, 18 stations
    python scripts/build_station_truth.py --stations KNYC,KPHX --start-year 2024
    python scripts/build_station_truth.py --no-era5-audit
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.truth.iem_cli import TRUTH_DIR, CliDay, IEMCliClient, kalshi_stations  # noqa: E402
from src.weather.open_meteo import OpenMeteoClient  # noqa: E402


def compact(d: CliDay) -> dict:
    return {
        "station": d.station, "valid": d.valid.isoformat(),
        "high": d.high_f, "low": d.low_f,
        "high_time": d.high_time, "low_time": d.low_time,
        "precip": d.precip_in, "precip_trace": d.precip_trace,
        "snow": d.snow_in, "snow_trace": d.snow_trace,
    }


def era5_audit(om: OpenMeteoClient, icao: str, meta: dict, truth: list[CliDay],
               start: date, end: date) -> dict:
    """Compare ERA5 (Open-Meteo archive) et CLI jour par jour."""
    obs = om.historical_observations(meta["lat"], meta["lon"], start, end, timezone=meta["tz"])
    era5 = {o.date: o for o in obs}
    rows: dict[str, list[tuple[float, float]]] = defaultdict(list)   # month → (era5, cli)
    for d in truth:
        o = era5.get(d.valid)
        if o is None:
            continue
        for var, cli_v, era_v in (("high", d.high_f, o.temperature_max),
                                  ("low", d.low_f, o.temperature_min)):
            if cli_v is None or era_v is None:
                continue
            rows[f"{var}:{d.valid.month:02d}"].append((era_v, float(cli_v)))
            rows[f"{var}:all"].append((era_v, float(cli_v)))
    out: dict = {}
    for k, pairs in sorted(rows.items()):
        diffs = [e - c for e, c in pairs]
        exact = sum(1 for e, c in pairs if round(e) == c)
        out[k] = {
            "n": len(pairs),
            "bias_era5_minus_cli_f": round(statistics.fmean(diffs), 2),
            "mae_f": round(statistics.fmean(abs(x) for x in diffs), 2),
            "sd_f": round(statistics.pstdev(diffs), 2) if len(diffs) > 1 else None,
            "exact_share": round(exact / len(pairs), 3),
            "share_off_by_2_or_more": round(sum(1 for x in diffs if abs(x) >= 2) / len(pairs), 3),
        }
    return out


def write_report(path: Path, audit: dict, span: tuple[date, date]) -> None:
    lines = [
        "# ERA5 vs CLI — audit de la vérité terrain / ground-truth audit",
        "",
        f"Période / span : {span[0]} → {span[1]}. Généré / generated : "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}.",
        "",
        "FR : ERA5 est ce que la climatologie du predictor a utilisé comme « observation ». "
        "CLI est ce qui résout les marchés Kalshi. Un biais non nul ou une part de jours "
        "à ≥ 2 °F d'écart élevée signifie que le modèle apprend à corriger la mauvaise cible.",
        "",
        "EN : ERA5 is what the predictor's climatology has used as 'observation'. CLI is what "
        "settles Kalshi markets. A non-zero bias or a high share of days off by ≥ 2 °F means "
        "the model has been learning to correct the wrong target.",
        "",
        "| Station | Var | n | biais ERA5−CLI (°F) | MAE (°F) | sd (°F) | jours exacts | ≥ 2 °F |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for icao, per in sorted(audit.items()):
        for var in ("high", "low"):
            r = per.get(f"{var}:all")
            if not r:
                continue
            lines.append(
                f"| {icao} | {var} | {r['n']} | {r['bias_era5_minus_cli_f']:+.2f} | {r['mae_f']:.2f} "
                f"| {r['sd_f']} | {r['exact_share']:.0%} | {r['share_off_by_2_or_more']:.0%} |"
            )
    lines += ["", "Détail mensuel dans `era5_vs_cli.json` / monthly detail in `era5_vs_cli.json`."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stations", default="", help="ICAO séparés par des virgules (défaut : 18 stations Kalshi)")
    ap.add_argument("--start-year", type=int, default=2018)
    ap.add_argument("--end-date", default=(date.today() - timedelta(days=1)).isoformat())
    ap.add_argument("--no-era5-audit", action="store_true")
    ap.add_argument("--out-dir", default=str(TRUTH_DIR))
    args = ap.parse_args()

    stations = kalshi_stations()
    wanted = [s.strip().upper() for s in args.stations.split(",") if s.strip()] or list(stations)
    unknown = [s for s in wanted if s not in stations]
    if unknown:
        print(f"Stations inconnues : {unknown}. Connues : {sorted(stations)}")
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    start = date(args.start_year, 1, 1)
    end = date.fromisoformat(args.end_date)

    cli = IEMCliClient(cache_dir=out_dir / "iem_cache")
    om = OpenMeteoClient()
    all_days: list[dict] = []
    summary: dict = {"schema": "station_truth_summary/1",
                     "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "span": [start.isoformat(), end.isoformat()], "stations": {}}
    audit: dict = {}

    for icao in wanted:
        meta = stations[icao]
        print(f"[{icao}] CLI {start} → {end} ...", flush=True)
        try:
            days = cli.fetch_range(icao, start, end)
        except Exception as e:  # noqa: BLE001 — on continue station suivante
            print(f"   ÉCHEC IEM : {e}")
            summary["stations"][icao] = {"error": str(e)}
            continue
        n_high = sum(1 for d in days if d.high_f is not None)
        summary["stations"][icao] = {
            "n_days": len(days), "n_high": n_high,
            "n_low": sum(1 for d in days if d.low_f is not None),
            "first": days[0].valid.isoformat() if days else None,
            "last": days[-1].valid.isoformat() if days else None,
        }
        print(f"   {len(days)} jours, {n_high} avec max")
        all_days.extend(compact(d) for d in days)
        if not args.no_era5_audit and days:
            try:
                audit[icao] = era5_audit(om, icao, meta, days, start, end)
                a = audit[icao].get("high:all", {})
                print(f"   ERA5 vs CLI (high) : biais {a.get('bias_era5_minus_cli_f')} °F, "
                      f"MAE {a.get('mae_f')} °F, exact {a.get('exact_share')}")
            except Exception as e:  # noqa: BLE001
                print(f"   audit ERA5 impossible : {e}")
                audit[icao] = {"error": str(e)}

    (out_dir / "cli_daily.json").write_text(json.dumps(all_days, separators=(",", ":")), encoding="utf-8")
    (out_dir / "truth_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if audit:
        (out_dir / "era5_vs_cli.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
        write_report(out_dir / "era5_vs_cli.md", audit, (start, end))
    print(f"\nÉcrit : {out_dir / 'cli_daily.json'} ({len(all_days)} lignes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
