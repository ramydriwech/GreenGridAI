# Phase 0 — exploration météo × éCO2mix (Aziz)

Le notebook exécutable et les cinq figures ci-dessous sont les résultats de l'exploration de 2024 réalisée sur Kaggle le **1er novembre 2026**. Les figures proviennent des sorties sauvegardées de ce notebook exécuté, sans recalcul dans cet export GitHub.

- [Notebook exécuté](../../notebooks/02_exploration_meteo_eco2mix_aziz.ipynb)
- [Notes de vérification](verified_handoff.md)
- [Résumé numérique exporté](evaluation1_evidence_summary.json)

## Figures

| Analyse | Résultat |
|---|---|
| Température vs consommation, France 2024 | [Nuage de points](../figures/aziz_phase0/fig_temp_vs_consumption_2024.png) |
| Vent 100 m (8 villes) vs intensité de production | [Nuage de points](../figures/aziz_phase0/fig_wind_vs_carbon_2024.png) |
| Variation saisonnière du rapport température–demande | [Analyse mensuelle](../figures/aziz_phase0/fig_temp_consumption_by_season_2024.png) |
| Archives à échéance fixe J−1 vs réanalyse ERA5, Paris | [Pilote météo](../figures/aziz_phase0/fig_previous_day1_vs_era5_pilot.png) |
| Vent → production éolienne → intensité CO₂ | [Diagnostics](../figures/aziz_phase0/fig_wind_proxy_vs_generation_and_carbon_2024.png) |

## Résultats de Phase 0

- 8 villes françaises et 70 272 observations météo ville-heure en 2024.
- 8 784 heures RTE + météo alignées, dont 8 783 paires valides pour les corrélations principales.
- Température–consommation : Pearson r = −0,575 sur 2024 ; relation fortement variable selon la saison.
- Vent (moyenne de 8 villes)–production éolienne : r = +0,861 ; production éolienne–intensité moyenne : r = +0,022.
- Paris, 1–7 octobre 2024, archive météo J−1 à 24 h : MAE de 0,950 °C pour la température et 4,138 km/h pour le vent 100 m sur 168 heures.
- Audit RTE 2024 : 4 horodatages UTC excédentaires en doublon, 4 créneaux de 15 min absents, 1 heure sans cible valide.

## Reproduction

1. Importer `notebooks/02_exploration_meteo_eco2mix_aziz.ipynb` dans Kaggle, avec Internet activé.
2. Exécuter **Run All** ; le notebook télécharge les données 2024 de RTE et Open-Meteo (ERA5 et Previous Runs), puis reconstruit les graphiques.
3. Consulter les CSV et figures générés dans `/kaggle/working/greengrid_phase0/`.

Les dépendances principales sont `pandas`, `numpy`, `matplotlib`, `requests`, `urllib3`, `jupyter`. Ne pas modifier le `requirements.txt` global de Ramy sans vérifier l'environnement commun.

## Précautions scientifiques

- **EDA exploratoire uniquement** : aucun modèle de prévision J+1 n'a été entraîné dans ce notebook.
- La réanalyse ERA5 aux heures futures n'est pas une prévision disponible à l'origine ; ne pas l'injecter comme variable future dans le modèle opérationnel.
- `previous_day1` signifie une échéance fixe de 24 h, et non un bulletin unique émis à heure fixe couvrant tous les horizons.
- La moyenne non pondérée de huit villes est un indicateur exploratoire, non une météo nationale représentative.
- Corrélation ≠ causalité. Le taux CO₂ RTE est une intensité moyenne de production, pas une intensité marginale.
- Le pilote parisien d'une semaine ne démontre pas de généralisation aux autres régions/saisons.
- 2025 reste réservé au test ; aucune donnée cible de 2025 n'a été interrogée dans le notebook.
- Les anomalies d'horodatage doivent être traitées/documentées avant l'entraînement.

**Sources des données :** [RTE éCO2mix](https://www.rte-france.com/eco2mix), [ERA5 via Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api), [Open-Meteo Previous Runs](https://open-meteo.com/en/docs/historical-forecast-api#previous-runs-api).
