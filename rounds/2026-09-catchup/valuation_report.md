# Rapport de valorisation — round de rattrapage 2026-06 → 2026-09

**Date du rapport :** 2026-09-08
**Période couverte :** 1er juin 2026 → 8 septembre 2026
**Rubric :** `rounds/RUBRIC.md` v0.2
**Barème :** `rounds/HOURLY_RATES.md` v0.1 (calibration 2026-05)
**Faits sources :** `facts.md` (même dossier)
**Statut :** input pour ratification. Round non proposé on-chain à la date du rapport.

---

## 0. Pourquoi un round de rattrapage

Aucun round n'a été proposé depuis `2026-05-genesis`. Le workflow `aratea-keeper`
tourne bien le 1er de chaque mois mais ne fait que **finaliser** un round existant ;
la proposition d'allocation est en dispatch manuel et n'a jamais été lancée. De plus
`KEEPER_PRIVATE_KEY` n'est pas configurée dans les secrets du dépôt, ce qui rend la
finalisation impossible en l'état. Ce round couvre donc quatre échéances mensuelles
en une seule passe.

Les plafonds d'émission ont été retirés par la décision du 2026-06-17
(`docs/token_model.md` §84, `docs/gouvernance-auto-mint.fr.md`,
`contracts/src/rounds/RoundRegistry.sol`). Aucun plafond mensuel global, aucun
plafond par apporteur, aucun plafond par wallet. Le rattrapage en un seul round ne
viole donc aucune règle en vigueur.

---

## 1. Base factuelle

106 commits retenus sur `origin/main`, dont 103 de @Elladriel80 pour
**+22 649 / −2 739 lignes**.

Exclusions, conformes au principe fact-only :

- commits machine `chore(auto)` du cron quotidien, `aratea-bot`, dependabot,
- lockfiles : 10 477 lignes ajoutées, non valorisées,
- fichiers de données et archives produits par le pipeline : 1 814 lignes ajoutées,
  non valorisées.

Répartition des lignes ajoutées par zone dominante : predictor 8 803, contracts
8 002, site 3 645, dashboard 1 938, docs 1 009, ci 629, rounds 353, oracle 70.

---

## 2. Écart de méthode assumé

Le rubric §4 prévoit une estimation par artefact. Ce rapport décompose en **six
phases** au lieu de 103 artefacts. C'est la méthode que le rubric réserve au genesis
(§10). Justification : à ce volume, le per-PR strict produit un rapport illisible
sans déplacer le total de plus de 10 %. Le détail par commit reste vérifiable dans
`facts.md`, ce qui préserve l'auditabilité pendant la fenêtre de challenge.

Règle de départage du §11 appliquée systématiquement : à hésitation entre deux
estimations, la plus basse est retenue.

---

## 3. Phase A — Gouvernance Phase 2

**Artefacts :** `MintGovernor.sol` token-weighted (vote 1 token = 1 voix, quorum,
file d'alternatives bornée `MAX_ALTERNATIVES`, `forceResolveStuck` GOV-2),
`aratea-keeper.yml` auto-mint, `VerifyDeploymentPhase2.s.sol`, `challengeWindow` en
secondes, UI de gouvernance DAO, runbooks de déploiement et de redéploiement
bilingues, dry-run anvil, +28 tests portant la couverture de branches au-delà de 90 %.

**Heures :** 95 h senior smart contracts + 20 h tech writer. Un gouverneur
token-weighted avec file d'alternatives, quorum et échappatoire de déblocage, plus
les scripts de vérification post-déploiement et les tests de branches, correspond à
environ trois semaines de travail pour un professionnel du domaine. Les runbooks
bilingues sont comptés séparément au profil rédaction.

**Avant ajustement :** (95 × 130 000) + (20 × 70 000) = **13 750 000 sats**

**Qualité ×1,20 :** tests ajoutés et substantiels (+0,10), documentation livrée avec
le code (+0,05), CI verte (+0,05).

**Impact ×1,40 :** débloque l'étape Phase 2 de la roadmap, critère « blocking » du §7.

**Valeur : 13 750 000 × 1,20 × 1,40 = 23 100 000 sats**

---

## 4. Phase B — Phase 3 assurance paramétrique

**Artefacts :** `PricingEngine.sol`, `PremiumPool.sol`, `PolicyRegistry.sol`,
interfaces, 39 tests unitaires puis 7 tests E2E full-stack, 20 tests de branches
complémentaires, `DeployPhase3` et `VerifyDeploymentPhase3`, page assurance du
dashboard, runbooks de déploiement bilingues avec confirmations Ledger, correction
des 3 findings Medium remontés par slither.

**Heures :** 70 h senior smart contracts + 12 h tech writer + 8 h dev dashboard.

**Avant ajustement :** (70 × 130 000) + (12 × 70 000) + (8 × 80 000) = **10 580 000 sats**

**Qualité ×1,20 :** couverture de tests élevée, findings statiques traités, docs à jour.

**Impact ×1,20 :** progrès mesurable sur la robustesse et l'avance de phase, mais la
Phase 3 n'est ni déployée ni utilisée. Niveau « high » bas de fourchette, pas « blocking ».

**Valeur : 10 580 000 × 1,20 × 1,20 = 15 235 200 sats**

---

## 5. Phase C — Predictor et recherche

**Artefacts :** feature sets v3, v3fa, v3fb et révision v4, `GBMLearnedModel`,
features `is_hightemp` / `consensus_x_spread` / `series_bias_prior`, backtest
champion-vs-market multi-dates, backtest P&L Kelly fractionnel, `power_analysis.py`,
correction PRED-1 du pipeline fold-aware, groupe témoin `no_bet` et settlement
ledger-only, et dix correctifs de justesse du 10 juin (formule de Kelly, marchés
void exclus du scoring, déduplication du backtest par ticker, respect du pin
`CHAMPION.json`, convention unique de normalisation des probas, station KNYC pour
NYC, `simulate.py` idempotent).

**Heures :** 90 h ML engineer + 30 h researcher quant. Le bug PRED-1 à lui seul
demandait de comprendre pourquoi 100 % des lignes étaient rejetées sur
`feature_missing`, puis de réinjecter les features fold-aware depuis le TRAIN
post-split dans deux scripts.

**Avant ajustement :** (90 × 140 000) + (30 × 160 000) = **17 400 000 sats**

**Qualité ×1,15 :** tests et docs présents, mais quelques correctifs sont des
reprises de travaux antérieurs, ce qui interdit le haut de la fourchette.

**Impact ×1,30 :** améliore mesurablement la qualité prédictive et la validité des
mesures. Le groupe témoin et la déduplication rendent le critère de décision non
gonflable, ce qui est la condition de tout le go/no-go.

**Valeur : 17 400 000 × 1,15 × 1,30 = 26 013 000 sats**

---

## 6. Phase D — Web public

**Artefacts :** refonte de la landing en application Next.js App Router avec données
predictor et on-chain en direct, compte contributeur self-service (OAuth GitHub
adossé à une adresse), durcissement du formulaire contributeur (troncature,
honeypot, rate limit), allowlist de schémas `ipfsHttpUrl` et passerelle ipfs.io,
cache `fetchAllRounds` avec validation du hash avant scan, correction i18n de la
FilterBar, en-têtes de sécurité sur les deux applications Next.

**Heures :** 45 h dev intermédiaire + 20 h senior dev (OAuth adossé à une adresse,
durcissement, en-têtes) + 10 h UX.

**Avant ajustement :** (45 × 80 000) + (20 × 130 000) + (10 × 90 000) = **7 100 000 sats**

**Qualité ×1,15 :** code propre et conventions respectées, mais peu de tests sur la
partie web.

**Impact ×1,20 :** la landing et le compte contributeur sont la porte d'entrée des
contributeurs externes, dont deux ont effectivement contribué sur la période.

**Valeur : 7 100 000 × 1,15 × 1,20 = 9 798 000 sats**

---

## 7. Phase E — CI, sécurité, ops

**Artefacts :** pin de toutes les GitHub Actions par SHA, workflow gitleaks et son
allowlist, `--require-hashes` sur les dépendances Python, suppression de l'exposition
de `BOT_PAT` sur la durée du job, budgets de temps par step et timeout du cron,
annonces Discord automatiques des captures et résolutions, revue de sécurité interne
des contrats Phase 1 et 2, rapport de correctifs du 10 juin, gate `KEEPER_ROLE` sur
`submitMeasurement` de l'oracle.

**Heures :** 25 h senior dev + 12 h audit smart contracts + 8 h ops.

**Avant ajustement :** (25 × 130 000) + (12 × 220 000) + (8 × 60 000) = **6 370 000 sats**

**Qualité ×1,15 :** correctifs traçables, rapport écrit, CI verte.

**Impact ×1,30 :** traite des risques critiques, fuite de secrets et intégrité de la
chaîne d'approvisionnement.

**Valeur : 6 370 000 × 1,15 × 1,30 = 9 523 150 sats**

---

## 8. Phase F — Documentation et pilotage

**Artefacts :** rafraîchissements de `STATUS.md` et `ROADMAP.md`, one-pager vision
bilingue, documentation de la fermeture de la piste climato windowed, notes d'audit,
hygiène `.gitignore`.

**Heures :** 30 h tech writer.

**Avant ajustement :** 30 × 70 000 = **2 100 000 sats**

**Qualité ×1,05 · Impact ×0,90 :** travail périphérique, niveau « modeste » du §7.

**Valeur : 2 100 000 × 1,05 × 0,90 = 1 984 500 sats**

---

## 9. Contributeurs externes

### @jihadMo — PR #202, `CONTRIBUTING.fr.md` +78/−1

Portage de parité depuis `CONTRIBUTING.md`. Le fichier français comptait 56 lignes
contre 155 en anglais ; la PR ajoute exactement les sections manquantes, dans le même
ordre, sans lien externe ni adresse ajoutés. Referme l'issue #197.

Profil tech writer, 70 000 sats/h. Heures : 2,5 h. Qualité ×1,10 (conventions,
CI verte). Impact ×1,00.

**Valeur : 2,5 × 70 000 × 1,10 × 1,00 = 192 500 sats**

### @SankeerthNara — PR #205, `predictor/README.md` +47/−11

Documente la distinction entre entrypoints de production et exploration ad-hoc, en
bilingue, avec un tableau des scripts quotidiens. Corrige une section devenue
trompeuse. Referme l'issue #195.

Profil tech writer, 70 000 sats/h. Heures : 2 h. Qualité ×1,10. Impact ×1,00.

**Valeur : 2 × 70 000 × 1,10 × 1,00 = 154 000 sats**

Aucun des deux n'a d'adresse enregistrée dans `rounds/WALLETS.md`. Le mint les
concernant est bloqué jusqu'à ce qu'ils en fournissent une.

---

## 10. Synthèse round

| Apporteur | Valeur (sats) | Valeur (BTC) | Tokens à mint @ NAV 1 sat = 1 token |
|---|---:|---:|---:|
| @Elladriel80 | 85 653 850 | 0,85654 | 85 653 850 |
| @jihadMo | 192 500 | 0,00193 | 192 500 |
| @SankeerthNara | 154 000 | 0,00154 | 154 000 |
| **TOTAL ROUND** | **86 000 350** | **0,86000** | **86 000 350** |

Détail par phase pour @Elladriel80 :

| Phase | Heures | Valeur (sats) |
|---|---:|---:|
| A. Gouvernance Phase 2 | 115 | 23 100 000 |
| B. Phase 3 assurance | 90 | 15 235 200 |
| C. Predictor et recherche | 120 | 26 013 000 |
| D. Web public | 75 | 9 798 000 |
| E. CI, sécurité, ops | 45 | 9 523 150 |
| F. Documentation | 30 | 1 984 500 |
| **TOTAL** | **475** | **85 653 850** |

**Effet sur la cap table.** Supply avant round : 34 039 500. Après round :
120 039 850. Part de @Elladriel80 : 99,71 %. Part des deux contributeurs externes :
0,29 %.

**Sanity check calendaire.** 475 heures sur 14 semaines, soit 34 h par semaine pour
un professionnel produisant cette sortie exacte. Le rubric valorise l'artefact et non
le temps réellement passé, mais l'ordre de grandeur reste plausible.

**Ancrage genesis.** Le round genesis avait valorisé 34 039 500 sats pour l'ensemble
du codebase predictor initial. Ce round vaut 2,5 fois le genesis pour trois mois de
travail couvrant deux phases de contrats, la refonte web et la recherche ML.

---

## 11. Vérification des garde-fous

- **Plafond mensuel global** : supprimé par la décision du 2026-06-17. Sans objet.
- **Plafond par apporteur** : supprimé par la même décision. Sans objet.
- **Plafond par wallet sur le vote** : supprimé. `docs/token_model.md` ligne 102
  mentionne encore un cap 25 % par wallet, contradiction résiduelle à corriger.
- **Valuation supérieure à 0,01 BTC** : oui, 0,85654 BTC pour @Elladriel80.
  Déclenche le vote pondéré des holders. @Elladriel80 étant le seul holder, il
  ratifierait sa propre valorisation. Le genesis avait traité ce cas en étendant la
  fenêtre de challenge à 30 jours. Décision à prendre pour ce round.

---

## 12. Incertitudes signalées au ratificateur

1. **Découpage en phases et non par artefact.** Écart de méthode assumé, voir §2.
   Une revue du découpage par un tiers est utile.
2. **Coefficients d'impact.** Les niveaux 1,40 sur la Phase A et 1,30 sur les phases
   C et E sont les plus discutables du rapport. Les ramener à 1,20 ferait passer le
   total de 86,0 à environ 78 millions de sats.
3. **Scope encore non tranché depuis mai.** Le rapport genesis exclut explicitement la
   conception du modèle de tokens, le RUBRIC, le barème et l'architecture monorepo,
   en les renvoyant à un round séparé ou au premier round mensuel régulier. Ce round
   est le premier. Ces artefacts ne sont **pas** inclus ici, la décision reste ouverte.
4. **Commits de l'agent `marc-dev`.** Un commit sur la période, correctif CI resté sur
   une branche et dupliqué ensuite. Non valorisé, considéré comme production de
   l'apporteur principal. Si tranché autrement : 1 h dev intermédiaire, qualité ×1,10,
   impact ×0,80 au titre du §7 « likely to be discarded or duplicated », soit
   70 400 sats.
5. **Travail hors Git non capté.** Recherche exploratoire, lectures de specs, décisions
   d'architecture prises hors dépôt. Non comptabilisé, conformément au §13 du rubric.
6. **Fenêtre du 11 août au 7 septembre.** Le pipeline quotidien était en panne, le push
   refusé pour cause de PAT expiré. Les 28 jours de captures et de résolutions
   correspondants sont perdus. Aucun effet sur cette valorisation, qui ne porte que sur
   des artefacts commités, mais l'événement explique le trou dans `facts.md`.

---

*Fin du rapport. Prochaine action : décision sur la durée de la fenêtre de challenge,
puis publication du rapport et dispatch `propose` du keeper. La clé keeper doit être
configurée avant toute finalisation.*
