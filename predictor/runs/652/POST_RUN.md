**Run 652 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Aug 10, 2026?
Bin cible : `KXLOWTNYC-26AUG10-B75.5` · Outcome : NO · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.318, Brier=0.1011, P&L réel=$-58.73
- `learned_v2` (challenger) — p_yes=0.614, Brier=0.3771, P&L théorique=$-58.73
- `kalshi_mid_baseline` (baseline) — p_yes=0.135, Brier=0.0182, P&L théorique=$-58.73 ⭐

Verdict run 652 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/652/report.json
