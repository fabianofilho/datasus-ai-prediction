"""Rótulo de abandono de TB a partir de SITUA_ENCE (PRED-01, DESF-01, DESF-02).

Mapa vigente: 1 cura, 2 abandono, 3 óbito por TB, 4 óbito por outras causas,
5 transferência, 6 mudança de diagnóstico, 7 TB-DR, 8 mudança de esquema,
9 falência, 10 abandono primário. Positivo {2, 10}; censura {5, 6, 7, 8}.
"""

from __future__ import annotations

import logging

import pandas as pd
import pytest

from core.data import sinan
from core.features.cohort import CohortBuilder
from core.outcomes.abandono_tb import AbandonoTB


def _ficha(codigos: list) -> pd.DataFrame:
    return pd.DataFrame({
        "SITUA_ENCE": codigos,
        "DT_ENCERRA": ["2021-06-30"] * len(codigos),
        "NU_IDADE_N": [4035] * len(codigos),
    })


@pytest.mark.parametrize("codigo", ["2", "10", " 2 ", "2.0", 10.0])
def test_abandono_e_abandono_primario_sao_positivos(codigo):
    df = sinan.preprocess(_ficha([codigo]))
    assert df["abandono"].tolist() == [1.0]


@pytest.mark.parametrize("codigo", ["1", "3", "4", "9"])
def test_cura_obitos_e_falencia_sao_negativos(codigo):
    df = sinan.preprocess(_ficha([codigo]))
    assert df["abandono"].tolist() == [0.0]


@pytest.mark.parametrize("codigo", ["5", "6", "7", "8"])
def test_censura_nao_vira_zero(codigo):
    df = sinan.preprocess(_ficha([codigo]))
    assert df["abandono"].isna().all()


def test_obito_por_tb_nao_e_mais_abandono():
    # Regressão do erro original: SITUA_ENCE 3 (óbito por TB) virava abandono.
    df = sinan.preprocess(_ficha(["1", "2", "3", "10"]))
    assert df["abandono"].tolist() == [0.0, 1.0, 0.0, 1.0]


def test_mapa_cobre_os_dez_codigos_sem_sobreposicao():
    assert set(sinan.SITUA_ENCE) == {str(i) for i in range(1, 11)}
    assert sinan.SITUA_ABANDONO == {"2", "10"}
    assert sinan.SITUA_CENSURA == {"5", "6", "7", "8"}
    assert not (sinan.SITUA_ABANDONO & sinan.SITUA_CENSURA)


def test_coorte_exclui_censura_e_reporta_contagem(caplog):
    codigos = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "", None]
    outcome = AbandonoTB()
    with caplog.at_level(logging.WARNING, logger="core.data.sinan"):
        coorte = outcome.build_cohort({"SINAN_TB": _ficha(codigos)})

    # 5 a 8, vazio e None saem; sobram 1, 2, 3, 4, 9, 10.
    assert sorted(coorte["SITUA_ENCE"].astype(str)) == sorted(["1", "2", "3", "4", "9", "10"])
    info = coorte.attrs["censura_abandono_tb"]
    assert info["n_excluidos"] == 6
    assert {k: info["por_codigo"][k] for k in ["5", "6", "7", "8"]} == {
        "5": 1, "6": 1, "7": 1, "8": 1,
    }
    assert "6 de 12 casos" in caplog.text

    y = outcome.get_target(coorte)
    assert y.dtype.kind == "i"
    assert dict(zip(coorte["SITUA_ENCE"].astype(str), y)) == {
        "1": 0, "2": 1, "3": 0, "4": 0, "9": 0, "10": 1,
    }


def test_get_xy_alinha_x_e_y_depois_da_censura():
    outcome = AbandonoTB()
    builder = CohortBuilder(outcome)
    coorte = builder.build({"SINAN_TB": _ficha(["1", "2", "5", "10", "7"])})
    X, y = builder.get_Xy(coorte)
    assert len(X) == len(y) == 3
    assert y.tolist() == [0, 1, 1]


def test_get_target_falha_se_sobrar_censura():
    outcome = AbandonoTB()
    coorte = sinan.preprocess(_ficha(["2", "5"]))
    with pytest.raises(ValueError, match="sem desfecho"):
        outcome.get_target(coorte)
