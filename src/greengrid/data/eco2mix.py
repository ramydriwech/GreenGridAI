"""Chargement des fichiers annuels éCO2mix (RTE) — national, données définitives.

Format réel des fichiers « .xls » téléchargés sur le site RTE :
  * texte tabulé encodé en latin-1 (pas un vrai classeur Excel) ;
  * une ligne d'avertissement juridique en fin de fichier ;
  * grille fixe de 96 créneaux de 15 min par jour en heure LOCALE (Europe/Paris),
    mais la plupart des colonnes (dont ``Taux de Co2``) ne sont renseignées
    qu'aux créneaux :00 et :30 → la vraie résolution est 30 min ;
  * changement d'heure de mars : l'heure 02:00–02:59 n'existe pas mais figure
    quand même dans le fichier (valeurs recopiées) → à supprimer ;
  * changement d'heure d'octobre : l'heure 02:00–02:59 existe deux fois mais
    n'apparaît qu'une fois → une heure réelle est absente.

Ce module ne fait que le chargement fidèle + passage en UTC. Le nettoyage
complet (imputation, calendrier) relève de la phase 1.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

TZ_LOCAL = "Europe/Paris"
TARGET = "co2_intensity"  # gCO2/kWh

#: Colonnes brutes RTE → noms normalisés (MW, sauf co2_intensity en gCO2/kWh).
COLUMN_MAP: dict[str, str] = {
    "Consommation": "consumption",
    "Prévision J-1": "forecast_d1",
    "Prévision J": "forecast_d0",
    "Fioul": "oil",
    "Charbon": "coal",
    "Gaz": "gas",
    "Nucléaire": "nuclear",
    "Eolien": "wind",
    "Solaire": "solar",
    "Hydraulique": "hydro",
    "Pompage": "pumping",
    "Bioénergies": "bioenergy",
    "Ech. physiques": "physical_exchanges",
    "Taux de Co2": TARGET,
    "Ech. comm. Angleterre": "exch_gb",
    "Ech. comm. Espagne": "exch_es",
    "Ech. comm. Italie": "exch_it",
    "Ech. comm. Suisse": "exch_ch",
    "Ech. comm. Allemagne-Belgique": "exch_de_be",
    "Fioul - TAC": "oil_tac",
    "Fioul - Cogén.": "oil_cogen",
    "Fioul - Autres": "oil_other",
    "Gaz - TAC": "gas_tac",
    "Gaz - Cogén.": "gas_cogen",
    "Gaz - CCG": "gas_ccg",
    "Gaz - Autres": "gas_other",
    "Hydraulique - Fil de l?eau + éclusée": "hydro_run_of_river",
    "Hydraulique - Lacs": "hydro_lakes",
    "Hydraulique - STEP turbinage": "hydro_step",
    "Bioénergies - Déchets": "bio_waste",
    "Bioénergies - Biomasse": "bio_biomass",
    "Bioénergies - Biogaz": "bio_biogas",
    "Stockage batterie": "battery_charge",
    "Déstockage batterie": "battery_discharge",
    "Eolien terrestre": "wind_onshore",
    "Eolien offshore": "wind_offshore",
}

#: Filières qui composent la production totale (hors pompage/stockage).
PRODUCTION_COLS = ["nuclear", "hydro", "wind", "solar", "gas", "coal", "oil", "bioenergy"]


def read_raw_file(path: str | Path) -> pd.DataFrame:
    """Lit un fichier annuel éCO2mix brut, sans modifier les valeurs.

    Returns:
        DataFrame avec ``ts_local`` (naïf, heure de Paris), ``nature`` et les
        colonnes renommées selon :data:`COLUMN_MAP`. Toutes les lignes
        (y compris :15/:45) sont conservées ; « ND » devient NaN.
    """
    df = pd.read_csv(
        path, sep="\t", encoding="latin-1", index_col=False,
        na_values=["ND", ""], low_memory=False,
    )
    df.columns = [c.strip() for c in df.columns]
    df = df[df["Nature"].notna()].copy()  # retire la ligne d'avertissement finale
    df["ts_local"] = pd.to_datetime(df["Date"] + " " + df["Heures"], format="%Y-%m-%d %H:%M")
    df = df.rename(columns={"Nature": "nature", **COLUMN_MAP})
    keep = ["ts_local", "nature"] + [c for c in COLUMN_MAP.values() if c in df.columns]
    out = df[keep]
    num = out.columns.drop(["ts_local", "nature"])
    out[num] = out[num].apply(pd.to_numeric, errors="coerce")
    return out.reset_index(drop=True)


def localize_to_utc(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Passe ``ts_local`` en UTC en traitant les changements d'heure.

    Conventions (à documenter dans la fiche dataset) :
      * heures inexistantes (mars) → lignes supprimées ;
      * heures ambiguës (octobre) → interprétées comme la 1re occurrence
        (heure d'été, CEST). L'heure réelle manquante reste un trou.

    Returns:
        (DataFrame indexé par ``ts_utc``, compteurs de lignes traitées).
    """
    loc = df["ts_local"].dt.tz_localize(
        TZ_LOCAL, ambiguous=np.ones(len(df), dtype=bool), nonexistent="NaT"
    )
    ambiguous = df["ts_local"].dt.tz_localize(
        TZ_LOCAL, ambiguous="NaT", nonexistent="NaT"
    ).isna() & loc.notna()
    stats = {"nonexistent_dropped": int(loc.isna().sum()), "ambiguous_as_cest": int(ambiguous.sum())}
    out = df.loc[loc.notna()].copy()
    out.index = pd.DatetimeIndex(loc[loc.notna()].dt.tz_convert("UTC"), name="ts_utc")
    return out.drop(columns="ts_local"), stats


def load_eco2mix(raw_dir: str | Path, years: Iterable[int]) -> pd.DataFrame:
    """Charge et concatène plusieurs années au pas natif 30 min, en UTC.

    Ne garde que les créneaux :00 et :30 (les :15/:45 sont vides pour
    l'intensité). Le fichier attendu est ``eCO2mix_RTE_Annuel-Definitif_<année>.xls``.
    """
    frames = []
    for y in years:
        raw = read_raw_file(Path(raw_dir) / f"eCO2mix_RTE_Annuel-Definitif_{y}.xls")
        raw = raw[raw["ts_local"].dt.minute.isin([0, 30])]
        utc, _ = localize_to_utc(raw)
        frames.append(utc)
    df = pd.concat(frames).sort_index()
    return df[~df.index.duplicated(keep="first")]


def to_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """Agrège au pas horaire (moyenne des créneaux disponibles, étiquette = début d'heure).

    Ajoute ``n_obs`` (nombre de demi-heures présentes, 0–2) pour tracer
    les heures incomplètes. Les heures absentes restent en NaN (pas d'imputation ici).
    """
    num = df.select_dtypes("number")
    hourly = num.resample("1h").mean()
    hourly["n_obs"] = num[TARGET].resample("1h").count()
    return hourly
