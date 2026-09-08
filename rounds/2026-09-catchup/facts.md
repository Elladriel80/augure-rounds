# Faits observables — round de rattrapage 2026-06 → 2026-09

Source : `git log origin/main --since=2026-06-01 --until=2026-09-09 --no-merges --numstat`.

Exclusions, conformes au principe fact-only du `RUBRIC.md` :

- commits machine `chore(auto)` du cron quotidien et commits `aratea-bot` / dependabot,
- lockfiles (`package-lock.json`, `requirements.lock`) : 10477 lignes ajoutées, non valorisées,
- fichiers de données et d'archives produits par le pipeline (`predictor/data/`, `predictor/runs/`, `runs_learning/`, `archives/`) : 1814 lignes ajoutées, non valorisées.

Périmètre retenu : **106 commits**, dont **103** de @Elladriel80 (+22649 / −2739 lignes) et **3** de contributeurs externes.

## Contributeurs externes

| Date | Auteur | Lignes | Zone | Sujet |
|---|---|---|---|---|
| 2026-08-08 | Sankeerth Nara | +47/−11 | predictor | docs(predictor): fix stale Structure block and document production entrypoints |
| 2026-08-07 | jihadMo | +78/−1 | docs | docs(contributing): bring CONTRIBUTING.fr.md up to parity with CONTRIBUTING.md (#197) |
| 2026-09-06 | marc-dev | +23/−10 | ci | fix(ci): daily-trading pousse avec GITHUB_TOKEN, plus de BOT_PAT |

## @Elladriel80 — détail par commit

| Date | SHA | Lignes | Fichiers | Zone | Sujet |
|---|---|---|---|---|---|
| 2026-05-19 | `7fabb2877` | +18/−8 | 2 | contracts | test(contracts): enforce MINTER_ROLE uniqueness via AccessControlEnumerable |
| 2026-05-19 | `2f534d078` | +12/−2 | 2 | contracts | chore(contracts): tighten foundry fs_permissions and remove parity bias in fuzz |
| 2026-05-19 | `ce401f13f` | +14/−28 | 2 | site | fix(site): remove ipapi.co geolocation fetch (RGPD), rely on navigator.language only |
| 2026-05-19 | `71f13c157` | +21/−4 | 2 | contracts | docs(security): align threat model with Phase 1 reality (solo EOA, role names) |
| 2026-05-19 | `63c6299ed` | +32/−19 | 3 | ci,docs | security(ci): switch execSync to execFileSync argv form + redact dead etherscan key |
| 2026-05-19 | `706d145b5` | +7/−4 | 1 | ci | ci(daily-trading): require pip hashes for supply-chain integrity (P3-NEW-1) |
| 2026-05-19 | `d149de28f` | +134/−12 | 2 | predictor | fix(daily_auto): fail hard on step exceptions instead of silent exit 0 |
| 2026-06-02 | `283108409` | +2/−10 | 1 | contracts | style(contracts): forge fmt MINTER_ROLE uniqueness test |
| 2026-06-02 | `105863cdf` | +1/−3 | 1 | contracts | style(contracts): forge fmt RoundRegistryFuzz.t.sol |
| 2026-06-02 | `4dfae7832` | +48/−32 | 3 | docs | docs(status): refresh STATUS/ROADMAP au 2026-06-02 (N>50 franchi, seuils reels, URLs) |
| 2026-06-02 | `a7fd04c8f` | +86/−0 | 1 | predictor | docs(predictor): acter la fermeture de la piste climato windowed (PIVOT_REJETE) |
| 2026-06-03 | `66be2e973` | +0/−0 | 1 | docs | chore(gitignore): ignore predictor scratch; repair mixed-encoding corruption |
| 2026-06-04 | `fe2c16705` | +4/−0 | 1 | site | fix(site): pin Vercel framework to nextjs so the App Router output is served |
| 2026-06-04 | `609844381` | +1718/−1314 | 29 | site | feat(site): rebuild landing as Next.js app (live predictor/on-chain data, wallet, contributor form, /roadmap, FR/EN) |
| 2026-06-05 | `2c8d9c16a` | +94/−1 | 2 | predictor | feat(predictor): persist ensemble feature components in run reports |
| 2026-06-05 | `6d0b29860` | +36/−9 | 1 | ci | fix(ci): daily-trading runs the learning capture again |
| 2026-06-05 | `bff3b82d3` | +1576/−0 | 2 | predictor | feat(predictor): champion-vs-market multi-date backtest |
| 2026-06-05 | `c5d102a17` | +230/−68 | 3 | predictor | feat(predictor): learned feature set v3 (collapse collinear probs, drop geo features) |
| 2026-06-10 | `b0a98f7ca` | +431/−0 | 1 | docs | docs: rapport correctifs revue 2026-06-10 |
| 2026-06-10 | `f81913459` | +353/−0 | 2 | rounds | fix(rounds): _xml_escape échappe aussi guillemets " et ' |
| 2026-06-10 | `059ca5362` | +13/−7 | 1 | ci | fix(ci): daily-trading n'expose plus BOT_PAT tout le job |
| 2026-06-10 | `0c7cf9ce5` | +29/−29 | 9 | ci | fix(ci): pin toutes les GitHub Actions par SHA de commit |
| 2026-06-10 | `6b833d454` | +102/−14 | 4 | dashboard | fix(dashboard): FilterBar statut value (brut) vs label (localisé) — fix FR |
| 2026-06-10 | `83f87defd` | +58/−0 | 4 | dashboard,site | fix(web): en-têtes de sécurité sur les deux apps Next |
| 2026-06-10 | `f77265a2f` | +90/−6 | 4 | dashboard | fix(dashboard): cache fetchAllRounds (60s) + valide le hash avant scan |
| 2026-06-10 | `5bb79166f` | +117/−6 | 4 | site | fix(site): durcissement formulaire contributeur (troncature + mentions + honeypot) |
| 2026-06-10 | `761cb5749` | +62/−7 | 4 | dashboard | fix(dashboard): ipfsHttpUrl allowlist de schémas + gateway ipfs.io |
| 2026-06-10 | `23bacf043` | +38/−4 | 2 | contracts | fix(contracts): challenges multiples (trace on-chain) sans changer la FSM |
| 2026-06-10 | `720356e27` | +66/−1 | 2 | contracts | fix(contracts): VerifyDeployment aligne le nom token sur l'on-chain |
| 2026-06-10 | `f63516245` | +70/−12 | 3 | oracle | fix(oracle): gate submitMeasurement par KEEPER_ROLE (AccessControl) |
| 2026-06-10 | `1c699f9e6` | +263/−1 | 2 | predictor | fix(predictor): marchés void exclus du scoring (pas comptés NO) |
| 2026-06-10 | `1e5621544` | +106/−2 | 2 | predictor | fix(predictor): simulate.py idempotent + ledger isolé (heat fantôme) |
| 2026-06-10 | `7c4c97d19` | +33/−1 | 2 | predictor | fix(predictor): NYC predit a la station de resolution KNYC (Central Park) |
| 2026-06-10 | `a3233618c` | +74/−6 | 2 | predictor | fix(predictor): formule Kelly correcte (f* = (p-px)/(1-px)) |
| 2026-06-10 | `d2607cc8c` | +136/−17 | 5 | predictor | fix(predictor): convention unique de normalisation des probas (live) |
| 2026-06-10 | `c4dff6590` | +196/−9 | 3 | predictor | fix(predictor): LearnedPredictor honore le pin de CHAMPION.json |
| 2026-06-10 | `73a5223d4` | +375/−17 | 4 | predictor | fix(predictor): dedup backtest par ticker (gate Phase B non gonflable) |
| 2026-06-11 | `e74c4b3e6` | +221/−1 | 3 | ci,predictor | feat(comms): annonces Discord auto des captures/resolutions + webhook recap dedie |
| 2026-06-11 | `cb555dc2d` | +20/−14 | 1 | predictor | fix(ci): budgets par step differencies — forward_predict 30 min (tue a 13 min le 11/06) |
| 2026-06-11 | `54ccdb20d` | +12/−3 | 2 | ci,predictor | fix(ci): daily-trading timeout 50 min + 13 min/step daily_run |
| 2026-06-17 | `45b770c23` | +2274/−31 | 20 | contracts,ci | feat(contracts): Phase 2 — auto-mint keeper + token-weighted MintGovernor |
| 2026-06-17 | `d7e67b70c` | +0/−38 | 1 | site | chore(site): supprime ContributeForm inutilise |
| 2026-06-17 | `00945c028` | +1/−5 | 1 | site | fix(site): section contribuer = seulement creer un compte contributeur (retire l'ancien formulaire + CTA GitHub/Discord du haut) |
| 2026-06-17 | `1b1c44ad6` | +1791/−4 | 24 | site,rounds | feat(site): self-service contributor account (GitHub OAuth ↔ wallet) |
| 2026-06-17 | `a5cd1b2b4` | +162/−2 | 2 | ci,contracts | chore(repo): exempt phase-b du stale bot + runbook deploiement Phase 1 |
| 2026-06-17 | `cb33e7959` | +113/−54 | 2 | predictor | fix(predictor): forward_predict ecriture incrementale + budget temps (fin du gel cron) |
| 2026-06-19 | `fc96605da` | +175/−16 | 3 | contracts,docs | fix(governor): quorum sur alternatives + plafond de file (MAX_ALTERNATIVES) |
| 2026-06-20 | `da8da1d6f` | +216/−0 | 2 | docs | docs(vision): one-pager bilingue FR/EN (B25) |
| 2026-06-20 | `7e60b9839` | +322/−0 | 2 | contracts | docs(ops): dry-run anvil local + checklist pre-vol (B21) |
| 2026-06-20 | `1bb736849` | +243/−0 | 2 | contracts | test(coverage): +28 tests MintGovernor + RoundRegistry → >90% branch coverage |
| 2026-06-20 | `a0077fed4` | +54/−0 | 1 | ci | fix(ci): add gitleaks secret-scanning workflow (revue 2026-06-10) |
| 2026-06-20 | `438eac5e8` | +64/−8 | 1 | predictor | docs(predictor): section bilingue FR/EN feature set v3 dans README |
| 2026-06-20 | `053082059` | +191/−3 | 3 | predictor | feat(predictor): GBMLearnedModel + features is_hightemp/consensus_x_spread |
| 2026-06-20 | `558f4b39e` | +1/−1 | 1 | predictor | fix(predictor): défaut --feature-set v0→v3 dans train_learned.py |
| 2026-06-20 | `efe7088c3` | +7/−4 | 1 | predictor | feat(predictor): bascule defaut sigma -> dispersion inter-modeles (7/7 dates, p=0.0078) |
| 2026-06-20 | `42478c81c` | +32/−6 | 1 | predictor | feat(predictor): sigma ensemble = dispersion inter-modeles (reglable env, defaut inchange) |
| 2026-06-21 | `39be5b360` | +715/−3 | 4 | contracts | fix(deploy): runbook redéploiement complet + dry-run FullStackRedeployTest (DEPLOY-1) |
| 2026-06-21 | `24b324a16` | +38/−6 | 2 | contracts | docs(runbooks): update Phase 2 runbook with VerifyDeploymentPhase2 script reference |
| 2026-06-21 | `4f1bdf9a0` | +77/−0 | 1 | contracts | feat(scripts): VerifyDeploymentPhase2 — post-deploy sanity check for Phase 2 wiring |
| 2026-06-21 | `83e461090` | +8/−4 | 1 | docs | chore(status): update test count 162→170 + security audit resolutions (PR #173) |
| 2026-06-21 | `186570e5b` | +227/−28 | 4 | contracts | fix(governor): forceResolveStuck escape hatch (GOV-2) + Phase 2 rewiring test (REG-1) |
| 2026-06-21 | `fec30b52d` | +7/−1 | 1 | docs | chore(status): B38 NO-GO documented + B39 universe expansion plan |
| 2026-06-21 | `88950489c` | +226/−0 | 4 | predictor | chore(predictor): archive learning runs + datasets (hygiene G4) |
| 2026-06-21 | `370ea1b61` | +173/−0 | 4 | predictor | feat(predictor): v3fb interaction features B38 — NO-GO on 62-date dataset |
| 2026-06-21 | `39e35887a` | +99/−183 | 1 | docs | docs(status): refresh STATUS.md au 2026-06-21 |
| 2026-06-21 | `b5e82e452` | +490/−18 | 7 | predictor | feat(predictor): v3fa feature set + algo_signal control group tracking (B35) |
| 2026-06-21 | `67b9ceb05` | +279/−0 | 4 | predictor | feat(predictor): feature révision v4 + annotation multi-captures (B23) |
| 2026-06-21 | `e32d3c4ac` | +284/−0 | 2 | contracts,docs | feat(security): revue de sécurité interne contrats Phase 1+2 (B33) |
| 2026-06-21 | `1058c04f0` | +1117/−7 | 8 | dashboard,contracts | feat(governance): Phase 2 deploy runbook + DAO governance UI |
| 2026-06-21 | `c9b34c53e` | +64/−0 | 1 | predictor | feat(predictor): feature v3b — series_bias_prior (calibration hiérarchique) |
| 2026-06-21 | `25cb3bf88` | +269/−0 | 1 | predictor | feat(predictor): backtest PnL / Kelly fractionnel sur runs résolus |
| 2026-06-22 | `efcfa8038` | +6/−1 | 1 | predictor | fix(geo): add missing city-ICAO mappings (Phoenix, Minneapolis +3) |
| 2026-06-22 | `06391bc55` | +35/−0 | 1 | contracts | docs(audit): add PRED-1 finding (fold-aware feature pipeline bug) |
| 2026-06-22 | `4e7652134` | +1314/−0 | 3 | predictor,docs | fix(predictor): exclude fold-aware features from backfill + inject at train time |
| 2026-06-23 | `aa0390ddf` | +23/−14 | 1 | docs | docs(predictor): STATUS.md -- second G2 run + power analysis (B54/B55) |
| 2026-06-23 | `d3fa7ab27` | +158/−0 | 1 | predictor | feat(predictor): power_analysis.py -- sample size for sign-test G2 |
| 2026-06-23 | `6889b66ae` | +14/−10 | 2 | ci,docs | fix(keeper): window_days → ROUND_WINDOW_SECONDS (désync B46) |
| 2026-06-23 | `b485317c0` | +400/−18 | 4 | contracts,docs | feat(phase3): Phase 3 Solidity interfaces scaffolding (B51) |
| 2026-06-23 | `2750c6918` | +11/−1 | 1 | ci | fix(ci): restrict gitleaks history scan to PR/new commits only |
| 2026-06-23 | `1cfd8db8c` | +192/−121 | 20 | contracts | feat(registry): challengeWindow en secondes — testnet UNE SESSION (B46) |
| 2026-06-24 | `018b7f8ce` | +418/−0 | 2 | contracts | docs(phase3): runbooks bilingues déploiement Phase 3 (5 confirmations Ledger, guide E2E test) |
| 2026-06-24 | `b0ec5cef6` | +5/−1 | 1 | docs | docs(status): Phase 3 deploy stack complete — B63 DeployPhase3 + MockOracle, B64 KeeperSettlePolicy, B65 /insurance UI |
| 2026-06-24 | `314833232` | +509/−4 | 9 | dashboard,contracts | feat(phase3): deploy scripts + dashboard insurance page |
| 2026-06-24 | `722b1876b` | +15/−2 | 1 | docs | docs(status): Phase 3 contracts in progress — 221 tests, B59-B62 |
| 2026-06-24 | `a67762260` | +1156/−0 | 5 | contracts | feat(phase3): PricingEngine + PremiumPool + PolicyRegistry + 39 tests |
| 2026-06-24 | `82614b789` | +49/−33 | 1 | contracts | refactor(phase3): update IPremiumPool interface for association AM model |
| 2026-06-26 | `88ad29be1` | +2/−2 | 1 | docs | docs(roadmap): M5 — Foundry installé, genesis à proposer via Ledger (~J+30 execute) |
| 2026-06-26 | `0a4434a8b` | +2/−2 | 1 | docs | docs(status): 2026-06-26 (B76) — 248 tests, couverture branches Phase 3 97-99% |
| 2026-06-26 | `eb9234b90` | +276/−0 | 1 | contracts | test(phase3): Phase3Coverage.t.sol — 20 tests branches manquantes (B76) |
| 2026-06-26 | `95758658a` | +26/−4 | 2 | docs | docs: G2 atteint + Phase 3 contrats complets (B74-B75) |
| 2026-06-26 | `6c3dab72a` | +6/−2 | 1 | docs | docs(status): 2026-06-26 -- 228 tests, Phase 3 E2E + VerifyDeploymentPhase3 (B67/B68) |
| 2026-06-26 | `275877325` | +132/−0 | 1 | contracts | feat(phase3): VerifyDeploymentPhase3.s.sol — post-deploy wiring sanity check (9 assertions) |
| 2026-06-26 | `cc566398e` | +332/−4 | 2 | contracts | test(phase3): FullStackPhase3E2E — 7 E2E integration tests + Phase 3 audit findings |
| 2026-07-02 | `ba08b48d4` | +11/−6 | 1 | docs | docs(status): STATUS.md — B77 security fixes, M5 confirmed, 248 tests, Phase 3 security findings |
| 2026-07-02 | `5e43a7371` | +30/−5 | 4 | contracts,predictor | sec(revue-2026-07-02): correctifs B77 — quotes isfinite, discord allowed_mentions, MockOracle keeper gate, anti-mock-mainnet |
| 2026-07-02 | `96068168c` | +7/−3 | 1 | ci | fix(ci): install gitleaks — asset checksums renommé upstream + curl -f |
| 2026-07-02 | `c3ec710e2` | +15/−0 | 1 | docs | fix(ci): .gitleaks.toml — allowlist des adresses Ethereum publiques (40 hex) |
| 2026-07-02 | `7b8a61a46` | +30/−2 | 3 | ci,docs | sec(revue-2026-07-02): quick wins — plage gitleaks push, rate limit formulaire contributeur, gitignore daily_log |
| 2026-07-03 | `7f692fa3a` | +95/−6 | 2 | docs,dashboard | docs(infra): checklist P1 (vars Vercel + secrets keeper) + ajoute NEXT_PUBLIC_GOVERNOR_ADDRESS a .env.example |
| 2026-07-03 | `5b7c6b1db` | +17/−14 | 3 | contracts,ci | fix(slither): corrige les 3 findings Medium Phase 3 + pin Foundry v1.7.1 |
| 2026-07-03 | `42291356a` | +452/−385 | 20 | contracts | fix(ci): forge fmt (forge 1.7.1) + pin Foundry v1.7.1 dans contracts-ci |
| 2026-07-31 | `332915b77` | +293/−5 | 2 | predictor | fix(phase1): câble le groupe témoin no_bet + settlement ledger-only |
| 2026-09-08 | `de84e33f3` | +1/−1 | 1 | ci | fix(ci): repasse le push sur BOT_PAT, jeton admin sans expiration |

## Agrégat par zone dominante (@Elladriel80)

| Zone | Lignes ajoutées | Lignes supprimées |
|---|---:|---:|
| contracts | 8002 | 696 |
| predictor | 7003 | 248 |
| site | 3645 | 1395 |
| dashboard | 1938 | 38 |
| docs | 1009 | 259 |
| ci | 629 | 91 |
| rounds | 353 | 0 |
| oracle | 70 | 12 |
| **TOTAL** | **22649** | **2739** |
