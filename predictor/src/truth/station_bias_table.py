"""Table de biais station pour le predictor / Station bias table for the predictor.

FR : Lit `data/truth/skill/station_bias.json` (produit chaque semaine par
scripts/eval_station_skill.py) et fournit (biais, sigma) pour une ville
Kalshi, une variable et un horizon. Utilisé par EnsemblePredictor quand
ARATEA_ENS_STATION_BIAS=1. Sans fichier ou sans entrée : renvoie None et le
predictor garde sa politique brute, jamais d'exception en production.

EN : Reads the weekly `station_bias.json` and serves (bias, sigma) for a
Kalshi city, variable and lead. Used by EnsemblePredictor behind
ARATEA_ENS_STATION_BIAS=1. Missing file or entry → None, raw policy kept.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .iem_cli import CITY_TO_ICAO, TRUTH_DIR

DEFAULT_PATH = TRUTH_DIR / "skill" / "station_bias.json"


class StationBiasTable:
    def __init__(self, path: Optional[Path] = None):
        # Resolution tardive : ARATEA_STATION_BIAS_PATH > DEFAULT_PATH du module.
        if path is None:
            path = os.environ.get("ARATEA_STATION_BIAS_PATH") or DEFAULT_PATH
        self.path = Path(path)
        self.entries: dict[tuple[str, str, int], tuple[float, float, int]] = {}
        self.loaded = False
        try:
            rows = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        for r in rows:
            try:
                self.entries[(r["station"], r["variable"], int(r["lead"]))] = (
                    float(r["bias_f"]), float(r["sigma_f"]), int(r.get("n_train", 0)))
            except (KeyError, TypeError, ValueError):
                continue
        self.loaded = bool(self.entries)

    def lookup(self, location_key: str, variable: str, days_ahead: int) -> Optional[tuple[float, float, int]]:
        """(biais °F à ajouter à mu, sigma résiduel °F, n) ou None.

        Le lead est borné à [1, 7] : une capture le jour même (J0) utilise le
        biais J-1, faute d'archive Previous Runs à lead 0."""
        icao = CITY_TO_ICAO.get(location_key)
        if icao is None:
            return None
        lead = min(7, max(1, int(days_ahead)))
        return self.entries.get((icao, variable, lead))
