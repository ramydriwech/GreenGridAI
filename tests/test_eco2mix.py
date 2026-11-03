"""Tests du chargement éCO2mix (nécessitent data/raw/ ; ignorés sinon)."""
from pathlib import Path

import pytest

from greengrid.data.eco2mix import TARGET, load_eco2mix, to_hourly

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
pytestmark = pytest.mark.skipif(not (RAW / "eCO2mix_RTE_Annuel-Definitif_2019.xls").exists(),
                                reason="fichiers éCO2mix absents")


def test_index_utc_unique_et_trie():
    df = load_eco2mix(RAW, [2019])
    assert str(df.index.tz) == "UTC"
    assert df.index.is_unique and df.index.is_monotonic_increasing


def test_changements_heure_2019():
    df = load_eco2mix(RAW, [2019])
    # 365 j x 48 demi-heures - 2 recopies (mars) ; octobre : 2 demi-heures manquantes
    assert len(df) == 365 * 48 - 2
    h = to_hourly(df)
    assert (h["n_obs"] == 0).sum() == 1  # l'heure perdue d'octobre
    assert h.loc[h["n_obs"] == 0].index[0].strftime("%Y-%m-%d %H") == "2019-10-27 01"


def test_cible_complete_et_plausible():
    df = load_eco2mix(RAW, [2019])
    assert df[TARGET].notna().all()
    assert df[TARGET].between(0, 200).all()
