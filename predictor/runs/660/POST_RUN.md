**Run 660 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Aug 10, 2026?
Bin cible : `KXLOWTCHI-26AUG10-B72.5` · Outcome : YES · Low observée (bin gagnant) : 72-73°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.178, Brier=0.6748, P&L réel=$-58.42
- `learned_v2` (challenger) — p_yes=0.250, Brier=0.5628, P&L théorique=$-58.42
- `kalshi_mid_baseline` (baseline) — p_yes=0.365, Brier=0.4032, P&L théorique=$-58.42 ⭐

Verdict run 660 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/660/report.json
