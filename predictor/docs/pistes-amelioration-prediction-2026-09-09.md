# Pistes d'amélioration du predictor Aratea

**Date :** 2026-09-09
**Portée :** predictor Phase 1 (marchés Kalshi température max/min, 18 stations US). Aucune incidence on-chain.
**Point de départ :** modèle v3 derrière `kalshi_mid` sur les deux fenêtres holdout, paper P&L +12,7 % non significatif (IC 95 % [-6,5 % ; +33,8 %]), holdout à ~13 dates pour 30 nécessaires. Journal de recherche v0.9 (2026-09-08) relu : recalibration NO-GO trois fois (l'écart au marché est informationnel), bascule sigma inter-modèles faite (Brier 0,116 → 0,098, deux tiers de l'écart comblés), 28 jours de données perdus en août.

---

## 1. Diagnostic : pourquoi on perd encore contre le marché

Cinq défauts structurels, par ordre d'impact estimé. Le journal a déjà tranché que le problème n'est pas la calibration mais l'information : les cinq points ci-dessous sont tous des apports d'information.

**1.1 On prédit une distribution avec des outils déterministes.** L'ensemble Aratea combine 5 sorties déterministes (IFS, AIFS single, GraphCast, GFS, JMA) et fabrique un sigma à partir de l'écart entre ces 5 valeurs. La bascule vers le sigma inter-modèles pur (juin) a prouvé que la dispersion réelle des modèles est le bon signal : c'est exactement ce qu'un vrai ensemble donne, en 51 membres au lieu de 5 points. Un contrat Kalshi est un bin de 2 °F : toute la valeur est dans la forme de la queue de distribution, qu'une gaussienne sur 5 points ne capture pas. Les ensembles (51 membres ECMWF IFS et AIFS, 31 GEFS, 64 WeatherNext 2) sont en accès libre. C'est la continuation naturelle du levier qui a marché.

**1.2 La vérité terrain utilisée n'est pas celle qui résout le marché.** La climatologie et le sigma sont calculés sur ERA5 (grille ~25 km, via Open-Meteo archive). Kalshi résout sur le rapport CLI du NWS, c'est-à-dire la station ASOS. Entre ERA5 et Central Park, Phoenix Sky Harbor ou Denver, il y a des biais de plusieurs °F, variables selon la saison. Le modèle apprend donc à corriger un biais qui n'est pas celui du contrat.

**1.3 Aucun post-processing station.** Toute la littérature opérationnelle (EMOS depuis 2005, réseaux distributionnels depuis Rasp & Lerch 2018) montre qu'un ensemble brut est sous-dispersé et biaisé localement, et que la correction station par station apporte 15 à 25 % de CRPS. Le NWS fait déjà ce travail pour toi : le National Blend of Models (NBM) publie des percentiles de MaxT/MinT calibrés par station, toutes les heures, gratuitement. On ne l'utilise pas.

**1.4 On ignore l'observation en cours de journée.** Un marché « high temp NYC aujourd'hui » à 15 h locale est essentiellement résolu : le max courant est connu à la minute via ASOS. Le predictor ne lit aucune observation temps réel. Les traders humains qui battent le marché sur les same-day le font avec ça.

**1.5 Le dataset d'évaluation est petit pour deux raisons qu'on peut attaquer, et une qu'on ne peut pas.** Le backfill Previous Runs × candlesticks existe déjà (`_backfill_dataset.py`, juin, 62 puis 86 dates). Ce qui le limite, d'après son propre `summary.json` :
- **Ce qu'on ne peut pas changer** : les marchés Kalshi température n'existent que depuis le 11 avril 2026. La comparaison au marché est bornée à ~5 mois, quoi qu'on fasse.
- **Ce qu'on peut changer (1)** : 5 374 lignes jetées pour `no_candle_at_capture`, soit 78 % des bins résolus. La capture simulée à 18:00 UTC pile exige une bougie horaire à cette heure ; prendre la dernière bougie disponible dans les 24 h précédant la capture, ou capturer à plusieurs heures, multiplie le dataset marché par 3 à 4 sans nouvelle donnée.
- **Ce qu'on peut changer (2)** : la fenêtre Previous Runs observée (~60 jours) fait tomber les dates anciennes. Le cache disque local est la seule mémoire. Il faut un snapshot quotidien automatique (cron GitHub Actions, réseau disponible), sinon chaque mois perdu l'est définitivement, comme les 28 jours d'août.
- **Ce qu'on n'exploite pas du tout** : la mesure de skill modèle vs vérité station ne dépend pas du marché. Avec la vérité CLI (IEM, pluriannuelle) et des bins synthétiques de 2 °F, on peut mesurer biais, sigma et Brier par station, par lead et par saison sur tout l'historique de prévisions disponible (HRRR AWS depuis 2014, NBM S3, GFS Previous Runs depuis 2021), et entraîner la correction station (B1) sur des années au lieu de semaines. Le marché ne sert alors qu'à la comparaison finale sur les 5 mois où il existe.

---

## 2. Pistes, classées par rapport effort / gain attendu

### Niveau A : à faire d'abord (gain probable, effort faible à moyen)

**A1. Remplacer la vérité ERA5 par la vérité station.**
Utiliser le CLI archivé (IEM `/json/cli.py`, par station, depuis des années, avec heure du max) comme cible d'entraînement et base de climatologie. Complément long terme : GHCN-Daily (NCEI) pour les stations USW (mêmes valeurs que le CLI, historique 30+ ans). Effet : la climatologie, le sigma et le `series_bias_prior` deviennent cohérents avec le contrat. C'est probablement ce qui explique une partie du biais KXHIGHTSFO à -0,09.

**A2. Ingérer le NBM (percentiles station).**
Bulletins texte NBP (percentiles 10/25/50/75/90 de MaxT/MinT par station, cycles 01/07/13/19 Z) et NBS/NBE (TXN déterministe + écart-type TSD). Archive quotidienne sur `s3://noaa-nbm-grib2-pds/blend.YYYYMMDD/HH/text/`. À tester d'abord comme predictor seul (P(bin) par interpolation des percentiles) puis comme feature. Hypothèse forte : NBM seul est proche de `kalshi_mid`, ce qui n'est pas le cas de notre ensemble actuel.

**A3. Passer aux vrais ensembles via l'Ensemble API Open-Meteo.**
Même client, même clé (gratuit non commercial). Modèles : ECMWF IFS 51 membres, ECMWF AIFS 51 membres, GEFS 31, GEM 21, MOGREPS-G 18, WeatherNext 2 64 membres. Construire P(bin) directement comme fraction de membres dans le bin après correction de biais station (A1). Le `forecast_spread` actuel devient l'écart-type des membres, ce qui a un sens physique.

**A4. Séparer le backtest « skill » du backtest « marché ».**
- Backtest skill (pluriannuel, sans marché) : prévisions à lead fixe (Previous Runs, HRRR AWS, NBM S3) × vérité CLI, sur bins synthétiques de 2 °F centrés comme les bins Kalshi. Sert à mesurer et corriger le biais station, le sigma par lead et par saison, et à entraîner B1. Des milliers de (station × date).
- Backtest marché (depuis avril 2026) : le `_backfill_dataset.py` existant, avec deux correctifs : garder la dernière bougie disponible avant capture au lieu d'exiger une bougie à 18:00 UTC pile (récupère la majorité des 5 374 lignes jetées), et faire tourner le snapshot Previous Runs en cron GitHub Actions pour ne plus perdre de dates.
Résultat : un holdout marché de 30 dates atteignable sur les données déjà existantes, et une mesure de skill indépendante du marché.

**A5. Modéliser la série complète de bins, pas chaque bin isolément.**
Les bins d'une série sont mutuellement exclusifs et exhaustifs. Prédire une distribution continue puis intégrer par bin garantit la cohérence (somme = 1) et permet de détecter les incohérences de prix entre bins (arbitrage intra-série), ce que la LR bin par bin ne voit pas.

### Niveau B : post-processing et apprentissage (gain moyen à fort, effort moyen)

**B1. EMOS / régression distributionnelle par station.**
Modèle : y ~ N(a + b·moyenne_ensemble, c + d·variance_ensemble), paramètres par station et par saison, ajustés par CRPS minimum. C'est la référence en post-processing. Version neurale (DRN, Rasp & Lerch 2018 ; variantes récentes avec pénalité de sharpness, arXiv 2606.08587) si le dataset A4 dépasse ~10 000 lignes. Benchmark public pour valider la méthode avant de l'appliquer : EUPPBench.

**B2. Traiter l'arrondi et le fuseau exactement comme le CLI.**
Le CLI travaille en heure standard locale (pas d'heure d'été : fenêtre 1 h à 0 h 59 en DST), en °F entier. Vérifier que `resolution.py` et le calcul de P(bin) alignent la fenêtre 24 h et la règle d'arrondi du NWS sur ce comportement. Un décalage d'une heure sur la fenêtre déplace le max de certains jours (fronts nocturnes).

**B3. Combiner avec le prix marché au lieu de le combattre.**
`kalshi_mid` est un estimateur meilleur que le nôtre. L'utiliser comme prior et n'apprendre que le résidu (stacking modèle + marché), puis ne miser que là où le modèle post-processé et le marché divergent d'un montant supérieur à l'erreur de calibration mesurée. Évite le piège documenté : un écart de 17 points modèle/marché reflète le plus souvent une incertitude que le modèle ignore.

**B4. Second marché comme signal.**
Polymarket a été écarté le 2026-05-14 faute de marchés météo récurrents. Ce n'est plus le cas : Polymarket cote aujourd'hui des marchés quotidiens de température max sur 44 villes. Le re-benchmark prévu le 2026-11-16 peut être avancé. L'écart Kalshi/Polymarket est une feature gratuite et parfois une opportunité d'arbitrage. Kalshi propose aussi des marchés horaires (source Weather Company) qui donnent une lecture continue de l'état du marché en journée.

### Niveau C : temps réel et haute résolution (gain fort sur same-day, effort moyen à élevé)

**C1. Nowcasting same-day sur ASOS.**
Sources : observations 5 min via `api.weather.gov/stations/{ICAO}/observations`, METAR via IEM (groupes de max 6 h à 00/06/12/18 Z), ASOS 1 minute (IEM/NCEI, rétrospectif, pour l'entraînement), dynamical.org ASOS/AWOS near-real-time. Logique : à l'heure h, P(max final dans le bin) = P(max courant dans le bin) × P(pas de dépassement d'ici minuit LST | prévision horaire HRRR + tendance observée). L'edge disparaît quand le marché a intégré l'info, donc automatiser la lecture est ce qui rend la chose exploitable. Contre-indication actuelle du bot : il ne trade pas les same-day parce qu'il n'a pas d'observation ; avec C1 la logique s'inverse.

**C2. HRRR pour J0/J1.**
3 km, horaire, 18 h et 48 h, archive AWS depuis 2014 (`noaa-hrrr-bdp-pds`, dynamical.org en zarr). Prévision horaire de T2m à la station, calibrée avec A1. Successeur RRFS en prototype sur AWS.

**C3. WeatherNext 3 (Google, août 2026).**
Nouveau : initialisation horaire, assimilation directe de satellites géostationnaires, 64 membres, grille 0,05° dédiée aux températures station, tables BigQuery `weathernext_3_0_0_0p05deg`, historique CC BY 4.0 au-delà d'une heure. Le seul modèle IA qui cible explicitement les températures de station. À évaluer en priorité dès que A4 fournit la vérité terrain. WeatherNext 2 est déjà exposé dans l'Ensemble API Open-Meteo.

**C4. ECMWF open data complet.**
Depuis 2025 tout le catalogue temps réel ECMWF est ouvert : IFS ENS 51 membres 0,25°, AIFS ENS. Accès direct par `ecmwf-opendata` ou en zarr via dynamical.org (CC BY-NC-SA, attention à la clause non commerciale pour la suite). Utile si on veut les membres bruts sans passer par Open-Meteo.

### Niveau D : idées à plus long terme (gain incertain, à ne pas engager avant A et B)

**D1. Lecture des Area Forecast Discussions du NWS par LLM** (déjà prévu en étage 2). Signal probable sur les jours de fort désaccord de modèles, faible sinon.
**D2. Features de régime** (ENSO, AO/NAO) : pertinentes pour l'horizon saisonnier, pas pour J+1 à J+7. À garder pour la mutuelle paramétrique, pas pour Kalshi.
**D3. Stations DePIN (WeatherXM)** : pas de valeur pour la résolution Kalshi (qui se fait à l'ASOS), valeur potentielle pour la Phase 3.
**D4. Conformal prediction** sur la P(bin) pour une garantie de couverture indépendante du modèle. Utile pour le sizing.

### Niveau E : cibles Phase 2 du journal (sécheresse, ouragans), données à préparer

Le journal fixe les cibles Tier 1 (sécheresse Méditerranée, US, Inde ; ouragans Atlantique formation / intensité / landfall) et la gate BSS > 0,05, avec backtest historique obligatoire. Rien à coder avant la preuve Kalshi, mais les sources existent et sont gratuites :

- **Prévisions saisonnières** : ECMWF SEAS5 et le multi-modèle C3S via le Climate Data Store (Copernicus, gratuit sur inscription), NMME (NOAA, multi-modèle nord-américain), Open-Meteo Seasonal API. Hindcasts 1981 à aujourd'hui, donc backtest possible sur 40 ans.
- **Sécheresse, vérité et indices** : SPEI global (CSIC), US Drought Monitor (archive hebdomadaire depuis 2000), ERA5-Land et GRACE (eau souterraine) pour les triggers paramétriques, CHIRPS pour les précipitations en Inde et Méditerranée.
- **Ouragans** : HURDAT2 et IBTrACS (trajectoires historiques, vérité), archives des prévisions NHC (a-decks/b-decks sur ftp.nhc.noaa.gov), prévisions saisonnières CSU et ECMWF, marchés Kalshi existants sur les ouragans comme benchmark.
- **Méthode** : les mêmes règles qu'en Phase 1 (split temporel, holdout gelé, comparaison à une référence). La référence naturelle n'est plus un marché mais la climatologie saisonnière et les prévisions officielles (CPC, ECMWF).

---

## 3. Données open source utilisables

| Besoin | Source | Accès | Couverture | Licence / coût |
|---|---|---|---|---|
| Vérité de résolution (CLI) | IEM `mesonet.agron.iastate.edu/json/cli.py` | JSON, par station | Pluriannuel, avec heure du max | Libre |
| Vérité longue (TMAX/TMIN station) | GHCN-Daily NCEI | CSV/API | 30+ ans, stations USW | Domaine public |
| Percentiles station calibrés | NBM NBP/NBS/NBE | `s3://noaa-nbm-grib2-pds/blend.YYYYMMDD/HH/text/` | Archive quotidienne, horaire | Domaine public |
| Ensembles (IFS, AIFS, GEFS, GEM, MOGREPS, WeatherNext 2) | Open-Meteo Ensemble API | REST, aucun compte | Prévision 10 à 16 j, 3 j de passé | Gratuit non commercial |
| Prévisions archivées à lead fixe | Open-Meteo Previous Runs API | REST | GFS depuis 2021, autres depuis 2024, J+1 à J+7 | Gratuit non commercial |
| Membres bruts IFS/AIFS ENS | ECMWF open data ; dynamical.org zarr | `ecmwf-opendata`, xarray/icechunk | Temps réel + archive dynamical | ECMWF CC BY 4.0 ; dynamical BY-NC-SA |
| Haute résolution J0/J1 | HRRR | `s3://noaa-hrrr-bdp-pds`, dynamical.org | Archive depuis 2014 | Domaine public |
| Observations temps réel | `api.weather.gov` observations ; IEM METAR/ASOS ; dynamical ASOS | REST | 5 min / horaire, temps réel | Libre |
| ASOS 1 minute (entraînement nowcast) | IEM / NCEI | CGI, CSV | Rétrospectif mensuel | Libre |
| MOS classique (GFS MEX/MAV) | IEM MOS archive | Web/CGI | Pluriannuel | Libre |
| Modèle IA station 0,05° | WeatherNext 3 | BigQuery, Earth Engine, GCS zarr | Temps réel (~2 h de latence), historique | CC BY 4.0 après 1 h ; coût BigQuery |
| Prix marché historiques | API Kalshi (candlesticks/trades) ; Lychee, Allium | REST | Depuis création des séries | API libre ; tiers payants |
| Second marché | Polymarket weather (44 villes) | API/Gamma | Temps réel | Libre |
| Benchmark méthodes post-processing | EUPPBench | Zarr | 122 stations Europe 2017-2018 | Libre |

---

## 4. Séquence proposée

1. **Semaine 1 : A1 + A4 (vérité et backtest).** Script de jonction CLI × Previous Runs × Kalshi historique sur les 18 stations. Livrable : dataset de plusieurs milliers de lignes, Brier `kalshi_mid` par horizon comme référence.
2. **Semaine 2 : A2 + A3 (NBM et ensembles).** Deux predictors nouveaux, évalués sur le dataset de l'étape 1. Question à trancher : NBM seul bat-il notre ensemble actuel ? Si oui, l'ensemble maison n'est plus le cœur du système.
3. **Semaine 3 : B1 + A5 (EMOS par station, distribution continue).** Un seul modèle produit la densité, les bins en découlent.
4. **Semaine 4 : B3 (stacking avec le marché) et règle de mise.** Ne miser que sur les écarts supérieurs à l'erreur de calibration mesurée. Relancer le groupe témoin `no_bet` avec ce modèle.
5. **Ensuite seulement : C1 (nowcast same-day), C3 (WeatherNext 3).**

Critère inchangé : Brier holdout < Brier `kalshi_mid`, sign-test p < 0,05, 30 dates minimum. La différence est qu'on peut l'atteindre en semaines, pas en mois.

---

## 5. Ce qui ne changera probablement rien

Pour éviter de rejouer des pistes closes : la climatologie pure (toutes fenêtres), les features géographiques statiques en terme additif, les interactions à petit échantillon. Ces NO-GO restent valides. Aucun modèle supplémentaire déterministe dans l'ensemble actuel n'apportera d'edge : le problème n'est pas le nombre de modèles, c'est l'absence de distribution et de calibration station.

---

## Sources

- Open-Meteo Ensemble API : https://open-meteo.com/en/docs/ensemble-api
- Open-Meteo Previous Runs API : https://open-meteo.com/en/docs/previous-runs-api
- Open-Meteo Historical Forecast API : https://open-meteo.com/en/docs/historical-forecast-api
- NBM sur AWS : https://registry.opendata.aws/noaa-nbm/
- NBM text archives : https://vlab.noaa.gov/web/mdl/nbm-text-archives
- NBM station card v5.0 (éléments TXN, TXNP1..P9) : https://vlab.noaa.gov/web/mdl/nbm-textcard-v5.0
- IEM CLI JSON : https://mesonet.agron.iastate.edu/json/cli.py?help=
- IEM ASOS 1 minute : https://mesonet.agron.iastate.edu/request/asos/1min.phtml
- IEM MOS archive : https://mesonet.agron.iastate.edu/mos/
- GHCN-Daily : https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily
- HRRR sur AWS : https://registry.opendata.aws/noaa-hrrr-pds/
- RRFS prototype : https://registry.opendata.aws/noaa-rrfs/
- dynamical.org catalogue (zarr IFS ENS, AIFS ENS, GEFS, HRRR, ASOS) : https://dynamical.org/catalog/
- ECMWF catalogue temps réel ouvert : https://www.ecmwf.int/en/about/media-centre/news/2025/ecmwf-makes-its-entire-real-time-catalogue-open-all
- AIFS ENS opérationnel : https://www.ecmwf.int/en/newsletter/185/earth-system-science/aifs-ens-becomes-operational
- WeatherNext 3 modèles : https://developers.google.com/weathernext/guides/models
- WeatherNext dissémination (BigQuery, GCS) : https://developers.google.com/weathernext/guides/dissemination
- Règles Kalshi weather (CLI, LST, DST) : https://help.kalshi.com/en/articles/13823837-weather-markets
- Guide trading wethr.net (CLI, DSM, METAR, fuseaux) : https://wethr.net/edu/trading-guide
- Guide stratégie Kalshi weather (pièges station, sigma, désaccord) : https://www.botforkalshi.com/blog/kalshi-weather-trading-strategy
- Polymarket weather : https://polymarket.com/weather/high-temperature
- Données Kalshi historiques : https://www.allium.so/blog/kalshi-historical-data-a-practical-guide/ ; https://lycheedata.com/kalshi-historical-data
- EUPPBench : https://essd.copernicus.org/articles/15/2635/2023/
- Journal de recherche Aratea v0.9 (Notion) : https://app.notion.com/p/Research-Journal-Climate-Event-Prediction-363472ba28fa8130bc88df73c61550de
- Post-processing neural, sharpness : https://arxiv.org/html/2606.08587
- Permutation-invariant NN post-processing : https://journals.ametsoc.org/view/journals/aies/3/1/AIES-D-23-0070.1.xml
