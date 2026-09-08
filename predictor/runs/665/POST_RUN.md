**Run 665 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Aug 10, 2026?
Bin cible : `KXLOWTPHX-26AUG10-B89.5` · Outcome : NO · Low observée (bin gagnant) : 85-86°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.192, Brier=0.0370, P&L réel=$+53.20 ⭐
- `learned_v2` (challenger) — p_yes=0.386, Brier=0.1490, P&L théorique=$+53.20
- `kalshi_mid_baseline` (baseline) — p_yes=0.475, Brier=0.2256, P&L théorique=$+53.20

Verdict run 665 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/665/report.json
