**Run 654 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Aug 10, 2026?
Bin cible : `KXLOWTNYC-26AUG10-B69.5` · Outcome : NO · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.026, Brier=0.0007, P&L réel=$+9.52 ⭐
- `learned_v2` (challenger) — p_yes=0.058, Brier=0.0034, P&L théorique=$+9.52
- `kalshi_mid_baseline` (baseline) — p_yes=0.140, Brier=0.0196, P&L théorique=$+9.52

Verdict run 654 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/654/report.json
