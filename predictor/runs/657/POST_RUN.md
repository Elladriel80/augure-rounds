**Run 657 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Aug 10, 2026?
Bin cible : `KXLOWTSFO-26AUG10-B57.5` · Outcome : YES · Low observée (bin gagnant) : 57-58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.401, Brier=0.3586, P&L réel=$-58.52
- `learned_v2` (challenger) — p_yes=0.257, Brier=0.5516, P&L théorique=$-58.52
- `kalshi_mid_baseline` (baseline) — p_yes=0.615, Brier=0.1482, P&L théorique=$-58.52 ⭐

Verdict run 657 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/657/report.json
