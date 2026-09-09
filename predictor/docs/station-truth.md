# Vérité station et skill hors marché / Station truth and market-free skill

**Date :** 2026-09-09 · **Portée :** predictor Phase 1 · **Origine :** note `pistes-amelioration-prediction-2026-09-09.md`, pistes A1 et A4.

## FR

### Le problème
Le predictor apprenait sur la mauvaise cible : la climatologie et le sigma étaient calculés sur ERA5 (grille 25 km, via Open-Meteo archive), alors que Kalshi résout sur le rapport climatologique quotidien (CLI) de la station ASOS. L'évaluation dépendait en plus de l'existence d'un marché coté, ce qui la bornait aux dates depuis avril 2026 et au lead J-1.

### Ce qui est ajouté
- `src/truth/iem_cli.py` : client de l'archive IEM des rapports CLI (`cli.py?station=KNYC&year=2026`), cache disque par année, mapping séries Kalshi → station → fuseau.
- `src/truth/lst_window.py` : fenêtre exacte du CLI (minuit à minuit en heure standard locale, jamais l'heure d'été). Toute agrégation horaire de prévision passe par là.
- `src/truth/synthetic_bins.py` : échelle de bins Kalshi (2 °F, queues) construite autour de la prévision, P(bin) gaussienne avec la correction d'arrondi ±0,5 °F.
- `src/truth/skill.py` : trois politiques scorées contre la vérité CLI (`raw` = production, `station_bias` = biais et sigma appris sur TRAIN par station/variable/lead, `climato` = CLI des années précédentes), split temporel, sign test par date.
- `src/weather/previous_runs.py` : client Previous Runs en version production (plages de dates, fuseau GMT, couverture mesurée).
- `scripts/build_station_truth.py` : collecte la vérité CLI des 18 stations et chiffre l'écart ERA5 vs CLI (`data/truth/era5_vs_cli.md`).
- `scripts/eval_station_skill.py` : backtest de skill hors marché (`data/truth/skill/skill_report.md`), paramètres de biais station (`station_bias.json`) et mémoire cumulative des prévisions agrégées (`forecast_points.json`).
- `.github/workflows/station-truth.yml` : exécution hebdomadaire sur le runner GitHub (réseau disponible), commit des sorties compactes.

### Ce que ça permet
1. Mesurer le biais ERA5 vs CLI par station et par mois : chiffrage du défaut, avant toute correction.
2. Mesurer le skill de la chaîne prévision → P(bin) par lead et par station sans attendre qu'un marché existe.
3. Obtenir des paramètres de correction station interprétables (deux nombres par station/variable/lead), prêts à être injectés dans `EnsemblePredictor` derrière un flag.
4. Ne plus perdre la fenêtre glissante Previous Runs : `forecast_points.json` fusionne à chaque run.

### Ce que ça ne fait pas
Pas de comparaison au marché (c'est le rôle de `_backfill_dataset.py`), pas de modification du predictor en production, pas de recalibration (NO-GO confirmé trois fois : l'apport ici est informationnel, pas cosmétique).

### Lancer en local
```bash
cd predictor
python scripts/build_station_truth.py --start-year 2020
python scripts/eval_station_skill.py
```
Réseau requis (IEM, Open-Meteo). Le workflow GitHub fait la même chose chaque lundi.

### Décision humaine à prendre ensuite
Si `skill_report.md` montre `station_bias` sous `raw` avec un sign test p < 0,05 sur ≥ 30 dates HOLDOUT, brancher la correction dans `EnsemblePredictor` (flag `ARATEA_ENS_STATION_BIAS`, défaut OFF) et relancer le backtest marché J-1.

## EN

### The problem
The predictor was learning against the wrong target: climatology and sigma came from ERA5 (25 km grid via Open-Meteo archive) while Kalshi settles on the station's NWS Daily Climate Report (CLI). Evaluation also required a quoted market, which limited it to dates since April 2026 and to the J-1 lead.

### What is added
IEM CLI client with yearly disk cache and series → station → timezone mapping; exact CLI window (local standard time, never daylight time); Kalshi-shaped synthetic bins with the ±0.5 °F rounding correction; three scoring policies (raw production, TRAIN-learned station bias, CLI climatology) with a temporal split and per-date sign test; a production-grade Previous Runs client; two scripts producing `data/truth/era5_vs_cli.md` and `data/truth/skill/skill_report.md` plus `station_bias.json`; a weekly GitHub workflow that runs them where network is available and commits the compact outputs, including the cumulative `forecast_points.json` memory.

### What it does not do
No market comparison (that stays in `_backfill_dataset.py`), no production predictor change, no recalibration (NO-GO confirmed three times; this is an information lever).

### Next human decision
If `skill_report.md` shows `station_bias` below `raw` with sign-test p < 0.05 over ≥ 30 HOLDOUT dates, wire the correction into `EnsemblePredictor` behind `ARATEA_ENS_STATION_BIAS` (default OFF) and rerun the J-1 market backtest.
