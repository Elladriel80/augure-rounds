**Run 646 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Aug 8, 2026?
Bin cible : `KXLOWTMIA-26AUG08-B79.5` · Outcome : NO · Low observée (bin gagnant) : 81-82°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.313, Brier=0.0979, P&L réel=$+39.90
- `learned_v2` (challenger) — p_yes=0.234, Brier=0.0549, P&L théorique=$+39.90 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.395, Brier=0.1560, P&L théorique=$+39.90

Verdict run 646 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/646/report.json
