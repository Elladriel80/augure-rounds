**Run 653 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Aug 10, 2026?
Bin cible : `KXLOWTNYC-26AUG10-B71.5` · Outcome : YES · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.123, Brier=0.7690, P&L réel=$-58.63
- `learned_v2` (challenger) — p_yes=0.125, Brier=0.7661, P&L théorique=$-58.63
- `kalshi_mid_baseline` (baseline) — p_yes=0.285, Brier=0.5112, P&L théorique=$-58.63 ⭐

Verdict run 653 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/653/report.json
