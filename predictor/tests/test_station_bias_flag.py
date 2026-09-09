"""Flag ARATEA_ENS_STATION_BIAS : table de biais + application dans EnsemblePredictor.
Hors ligne : client météo simulé."""
from __future__ import annotations

import json
from datetime import date, timedelta

import pytest

from src.predictors.base import ContractSpec
from src.predictors.ensemble import EnsemblePredictor
from src.truth.station_bias_table import StationBiasTable
from src.weather.open_meteo import DailyForecast


def _table(tmp_path, rows):
    p = tmp_path / "station_bias.json"
    p.write_text(json.dumps(rows), encoding="utf-8")
    return StationBiasTable(p)


def test_table_lookup_maps_city_and_clamps_lead(tmp_path):
    t = _table(tmp_path, [
        {"station": "KLAX", "variable": "temp_max", "lead": 1, "bias_f": -3.5, "sigma_f": 2.7, "n_train": 83},
        {"station": "KLAX", "variable": "temp_max", "lead": 7, "bias_f": -4.0, "sigma_f": 2.9, "n_train": 83},
    ])
    assert t.loaded
    assert t.lookup("LOSANGELES", "temp_max", 1) == (-3.5, 2.7, 83)
    assert t.lookup("LOSANGELES", "temp_max", 0) == (-3.5, 2.7, 83)      # J0 → J-1
    assert t.lookup("LOSANGELES", "temp_max", 12) == (-4.0, 2.9, 83)     # borné à 7
    assert t.lookup("LOSANGELES", "temp_min", 1) is None
    assert t.lookup("VILLE_INCONNUE", "temp_max", 1) is None


def test_table_missing_file_is_silent(tmp_path):
    t = StationBiasTable(tmp_path / "absent.json")
    assert not t.loaded and t.lookup("NYC", "temp_max", 1) is None


class _FakeWeather:
    """Sert des observations historiques constantes et des modèles à 70/72 °F."""
    def __init__(self, target):
        self.target = target

    def historical_observations(self, lat, lon, start, end, timezone="auto"):
        from src.weather.open_meteo import DailyObservation
        out, d = [], start
        while d <= end:
            out.append(DailyObservation(d, 71.0 + (d.day % 3), 55.0, 0.0, 0.0, {}))
            d += timedelta(days=1)
        return out

    def historical(self, *a, **kw):  # pragma: no cover
        raise AssertionError("not used")

    def forecast_multi_model(self, lat, lon, models=None, days=7, timezone="auto", use_cache=True):
        return {m: [DailyForecast(m, self.target, 70.0 if i == 0 else 72.0, 50.0, 0.0, 0.0, 0.0)]
                for i, m in enumerate(models or ["ecmwf_ifs025", "gfs_global"])}


def _contract(target):
    return ContractSpec("KXHIGHTLAX-T", "KXHIGHTLAX", "temp_max", "LOSANGELES", target, 66, 67, "66° to 67°")


def test_flag_off_by_default_and_on_via_env(tmp_path, monkeypatch):
    target = date.today() + timedelta(days=1)
    weather = _FakeWeather(target)
    monkeypatch.delenv("ARATEA_ENS_STATION_BIAS", raising=False)
    off = EnsemblePredictor(weather_client=weather, models=["ecmwf_ifs025", "gfs_global"])
    assert off.station_bias_table is None
    p_off = off.predict(_contract(target))
    assert p_off.inputs["station_bias"] is None
    assert p_off.inputs["mu"] == 71.0

    rows = [{"station": "KLAX", "variable": "temp_max", "lead": 1, "bias_f": -4.0, "sigma_f": 1.5, "n_train": 83}]
    (tmp_path / "station_bias.json").write_text(json.dumps(rows), encoding="utf-8")
    monkeypatch.setattr("src.truth.station_bias_table.DEFAULT_PATH", tmp_path / "station_bias.json")
    monkeypatch.setenv("ARATEA_ENS_STATION_BIAS", "1")
    on = EnsemblePredictor(weather_client=weather, models=["ecmwf_ifs025", "gfs_global"])
    p_on = on.predict(_contract(target))
    assert p_on.inputs["station_bias"] == {"bias_f": -4.0, "sigma_f": 1.5, "n_train": 83}
    assert p_on.inputs["mu"] == 67.0 and p_on.inputs["sigma_total"] == 1.5
    # mu corrigé tombe dans le bin 66-67 : P(YES) doit grimper nettement
    assert p_on.prob_yes > p_off.prob_yes + 0.3


def test_flag_on_without_entry_keeps_raw_policy(tmp_path, monkeypatch):
    target = date.today() + timedelta(days=1)
    (tmp_path / "station_bias.json").write_text("[]", encoding="utf-8")
    monkeypatch.setattr("src.truth.station_bias_table.DEFAULT_PATH", tmp_path / "station_bias.json")
    on = EnsemblePredictor(weather_client=_FakeWeather(target), models=["ecmwf_ifs025", "gfs_global"], station_bias=True)
    p = on.predict(_contract(target))
    assert p.inputs["station_bias"] is None and p.inputs["mu"] == 71.0
