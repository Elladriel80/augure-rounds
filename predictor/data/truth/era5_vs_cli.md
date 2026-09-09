# ERA5 vs CLI — audit de la vérité terrain / ground-truth audit

Période / span : 2020-01-01 → 2026-09-08. Généré / generated : 2026-09-09T06:27:04Z.

FR : ERA5 est ce que la climatologie du predictor a utilisé comme « observation ». CLI est ce qui résout les marchés Kalshi. Un biais non nul ou une part de jours à ≥ 2 °F d'écart élevée signifie que le modèle apprend à corriger la mauvaise cible.

EN : ERA5 is what the predictor's climatology has used as 'observation'. CLI is what settles Kalshi markets. A non-zero bias or a high share of days off by ≥ 2 °F means the model has been learning to correct the wrong target.

| Station | Var | n | biais ERA5−CLI (°F) | MAE (°F) | sd (°F) | jours exacts | ≥ 2 °F |
|---|---|---|---|---|---|---|---|
| KATL | high | 2440 | -2.35 | 2.84 | 2.35 | 8% | 67% |
| KATL | low | 2439 | -1.77 | 2.15 | 1.97 | 12% | 49% |
| KAUS | high | 2443 | -1.63 | 2.56 | 2.69 | 10% | 57% |
| KAUS | low | 2443 | +4.05 | 4.46 | 3.96 | 8% | 70% |
| KBOS | high | 2440 | -1.04 | 2.10 | 2.46 | 14% | 45% |
| KBOS | low | 2440 | -0.92 | 1.96 | 2.35 | 16% | 42% |
| KDEN | high | 2443 | -1.84 | 2.88 | 3.13 | 9% | 61% |
| KDEN | low | 2443 | +2.65 | 3.60 | 3.81 | 10% | 64% |
| KIAH | high | 2441 | -2.64 | 3.10 | 2.64 | 9% | 67% |
| KIAH | low | 2441 | +0.12 | 1.82 | 2.36 | 17% | 38% |
| KLAS | high | 2441 | -0.50 | 1.23 | 1.58 | 29% | 20% |
| KLAS | low | 2440 | -2.08 | 2.66 | 2.46 | 9% | 60% |
| KMIA | high | 2433 | -2.26 | 2.47 | 1.84 | 9% | 59% |
| KMIA | low | 2433 | -2.16 | 2.59 | 2.24 | 10% | 58% |
| KMSP | high | 2443 | -1.25 | 2.15 | 2.42 | 15% | 47% |
| KMSP | low | 2443 | -1.62 | 2.35 | 2.66 | 15% | 47% |
| KNYC | high | 2441 | -0.89 | 1.98 | 2.38 | 17% | 43% |
| KNYC | low | 2441 | -2.55 | 3.11 | 3.16 | 11% | 59% |
| KORD | high | 2443 | -1.65 | 2.27 | 2.24 | 12% | 51% |
| KORD | low | 2443 | -1.81 | 2.37 | 2.41 | 14% | 51% |
| KPHL | high | 2443 | -1.09 | 1.92 | 2.16 | 16% | 42% |
| KPHL | low | 2443 | -1.47 | 2.16 | 2.35 | 15% | 47% |
| KPHX | high | 2440 | -2.22 | 2.36 | 1.78 | 10% | 54% |
| KPHX | low | 2440 | -2.85 | 3.20 | 2.48 | 7% | 70% |
| KSAT | high | 2441 | -2.01 | 2.67 | 2.56 | 11% | 60% |
| KSAT | low | 2443 | +0.15 | 2.05 | 2.66 | 14% | 43% |
| KSFO | high | 2429 | -1.23 | 2.54 | 2.9 | 12% | 58% |
| KSFO | low | 2436 | -1.24 | 1.82 | 1.88 | 16% | 40% |

Détail mensuel dans `era5_vs_cli.json` / monthly detail in `era5_vs_cli.json`.
