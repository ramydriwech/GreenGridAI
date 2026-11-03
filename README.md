# GreenGrid AI

Prévision horaire de l'intensité carbone du réseau électrique français (RTE éCO2mix) à J+1 (1–48 h)
et recommandation de fenêtres bas-carbone pour décaler des tâches flexibles.
Projet tutoré SUP'COM — Ramy & Aziz.

## Structure

```
data/raw/            fichiers éCO2mix bruts (non versionnés, voir ci-dessous)
notebooks/           exploration uniquement (01_exploration_eco2mix.ipynb)
src/greengrid/       code réutilisable (data/eco2mix.py : chargement + UTC + pas horaire)
tests/               tests pytest
reports/figures/     figures générées par les notebooks
```

## Données

Télécharger sur RTE éCO2mix les fichiers « Données annuelles définitives » France 2019–2025
(`eCO2mix_RTE_Annuel-Definitif_<année>.xls`) et les placer dans `data/raw/`.

## Règles du projet

- Découpage figé : **train 2019–2023, validation 2024, test 2025** (verrouillé jusqu'au 4 janv. 2027).
- Métriques : MAE, RMSE (gCO₂/kWh), couverture des intervalles, regret de la recommandation.
- Tout modèle doit battre la persistance J-1.

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
```
