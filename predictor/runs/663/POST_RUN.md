**Run 663 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Aug 10, 2026?
Bin cible : `KXLOWTBOS-26AUG10-B66.5` · Outcome : NO · Low observée (bin gagnant) : ≥67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.034, Brier=0.0011, P&L réel=$+6.17 ⭐
- `learned_v2` (challenger) — p_yes=0.058, Brier=0.0034, P&L théorique=$+6.17
- `kalshi_mid_baseline` (baseline) — p_yes=0.095, Brier=0.0090, P&L théorique=$+6.17

Verdict run 663 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/663/report.json
