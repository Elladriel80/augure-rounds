"""Smoke hors ligne de scripts/eval_station_bias_market.py sur les données
suivies du repo (forward_*.json, cli_daily.json, forecast_points.json)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import eval_station_bias_market as m

TRUTH = Path(__file__).resolve().parents[1] / "data" / "truth"


@pytest.mark.skipif(not (TRUTH / "cli_daily.json").exists() or not (TRUTH / "skill" / "forecast_points.json").exists(),
                    reason="données truth absentes (premier run du workflow non encore commité)")
def test_market_backtest_runs_and_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["x", "--min-date", "2026-08-01", "--out-dir", str(tmp_path)])
    assert m.main() == 0
    run = json.loads((tmp_path / "market_backtest.json").read_text(encoding="utf-8"))
    o = run["overall"]["all"]
    assert run["n_rows"] > 100 and 0 < o["brier_market"] < 0.25
    assert set(run["by_lead"]) <= {0, 1, 2, 3, "0", "1", "2", "3"}
    assert "station_vs_market" in run["sign_tests"]
    assert (tmp_path / "market_backtest.md").read_text(encoding="utf-8").startswith("# Correction station")


def test_point_in_time_bias_uses_only_past_targets():
    from datetime import date
    pts = [{"station": "K", "variable": "temp_max", "lead": 1, "_target": date(2026, 6, d), "_mean": 70.0}
           for d in range(1, 26)]
    truth = {("K", date(2026, 6, d)): {"high": 72} for d in range(1, 26)}
    b = m.PointInTimeBias(pts, truth)
    assert b.get("K", "temp_max", 1, date(2026, 6, 10)) is None            # 9 paires < 20
    got = b.get("K", "temp_max", 0, date(2026, 6, 26))                      # lead 0 → 1
    assert got is not None and abs(got[0] - 2.0) < 1e-9 and got[2] == 25
