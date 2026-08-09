**Run 641 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Aug 8, 2026?
Bin cible : `KXLOWTSFO-26AUG08-B59.5` · Outcome : NO · Low observée (bin gagnant) : 57-58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.440, Brier=0.1940, P&L réel=$-61.25
- `learned_v2` (challenger) — p_yes=0.740, Brier=0.5468, P&L théorique=$-61.25
- `kalshi_mid_baseline` (baseline) — p_yes=0.245, Brier=0.0600, P&L théorique=$-61.25 ⭐

Verdict run 641 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/641/report.json
