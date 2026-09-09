"""Bout-en-bout hors ligne de scripts/eval_station_skill.py : réseau simulé
(IEM + Previous Runs), vérifie que le rapport et les JSON sont produits et
cohérents. Le vrai run réseau se fait en local ou dans le workflow
`station-truth.yml`."""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone

import pytest

import eval_station_skill as ess  # via conftest sys.path (scripts/)
from src.truth import iem_cli
from src.weather import open_meteo


def _fake_cli_year(station: str, year: int) -> dict:
    res = []
    d = date(year, 1, 1)
    while d.year == year:
        # max ≈ 60 + saison ; les modèles (ci-dessous) sous-estiment de 2 °F
        hi = 60 + 15 * (1 if 120 <= d.timetuple().tm_yday <= 270 else 0) + (d.day % 5)
        res.append({"valid": d.isoformat(), "station": station, "high": hi, "low": hi - 15})
        d += timedelta(days=1)
    return {"results": res}


def _fake_prev_runs(base: str, params: dict) -> dict:
    start = date.fromisoformat(params["start_date"])
    end = date.fromisoformat(params["end_date"])
    n_hours = ((end - start).days + 1) * 24
    t0 = datetime(start.year, start.month, start.day, tzinfo=timezone.utc)
    times = [(t0 + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(n_hours)]
    hourly = {"time": times}
    models = params["models"].split(",")
    for var in params["hourly"].split(","):
        for m in models:
            vals = []
            for i in range(n_hours):
                day = (t0 + timedelta(hours=i)).date()
                hi = 60 + 15 * (1 if 120 <= day.timetuple().tm_yday <= 270 else 0) + (day.day % 5)
                # profil diurne : pic à 20 UTC ; biais -2 °F ; petit écart inter-modèles
                diurnal = -8 if (i % 24) < 12 else 0
                vals.append(hi - 2 + diurnal + (0.5 if m.endswith("025") else -0.5))
            hourly[f"{var}_{m}"] = vals
    return {"hourly": hourly}


def test_eval_station_skill_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setattr(iem_cli.IEMCliClient, "_fetch_year_raw",
                        lambda self, station, year: _fake_cli_year(station, year))
    monkeypatch.setattr(open_meteo.OpenMeteoClient, "_get",
                        lambda self, base, params: _fake_prev_runs(base, params))
    monkeypatch.setattr(iem_cli, "TRUTH_DIR", tmp_path)
    monkeypatch.setattr(ess, "TRUTH_DIR", tmp_path)
    real_prev = ess.PreviousRunsClient
    monkeypatch.setattr(ess, "PreviousRunsClient",
                        lambda **kw: real_prev(cache_dir=tmp_path / "prev", sleep_s=0, **kw))

    out_dir = tmp_path / "skill"
    argv = ["eval_station_skill.py", "--stations", "KNYC,KPHX", "--leads", "1,2",
            "--models", "gfs_global,ecmwf_ifs025",
            "--start", "2026-05-01", "--end", "2026-07-30", "--out-dir", str(out_dir)]
    monkeypatch.setattr(sys, "argv", argv)
    assert ess.main() == 0

    run = json.loads((out_dir / "skill_run.json").read_text(encoding="utf-8"))
    assert run["n_points_holdout"] > 0 and run["n_bins_scored"] > 0
    overall = run["overall"]["all"]
    # biais systématique -2 °F : la correction station doit battre raw et la climato
    assert overall["brier_station"] < overall["brier_raw"]
    assert overall["brier_station"] < overall["brier_climo"]
    biases = json.loads((out_dir / "station_bias.json").read_text(encoding="utf-8"))
    hi_b = [b for b in biases if b["variable"] == "temp_max"]
    assert hi_b and all(1.5 < b["bias_f"] < 2.5 for b in hi_b)
    report = (out_dir / "skill_report.md").read_text(encoding="utf-8")
    assert "Par lead" in report and "KNYC" in report and "KPHX" in report
    assert run["sign_tests"]["station_vs_raw"]["p_one_sided"] < 0.05
