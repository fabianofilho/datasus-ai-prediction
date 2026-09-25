"""CLASSI_FIN da dengue no layout vigente (PRED-02, DESF-03).

5 descartado, 8 inconclusivo, 10 dengue, 11 dengue com sinais de alarme,
12 dengue grave, 13 chikungunya. Coorte = {10, 11, 12}; positivo = {11, 12}.
"""

from __future__ import annotations

import pandas as pd
import pytest

from core.data import sinan_deng
from core.outcomes.dengue_grave import DengueGrave


def _fichas(codigos: list) -> pd.DataFrame:
    return pd.DataFrame({
        "CLASSI_FIN": codigos,
        "NU_IDADE_N": [4030] * len(codigos),
        "CS_SEXO": ["F"] * len(codigos),
    })


@pytest.mark.parametrize(
    "codigo, confirmado, grave",
    [
        ("5", 0, 0),    # descartado
        ("8", 0, 0),    # inconclusivo
        ("10", 1, 0),   # dengue
        ("11", 1, 1),   # dengue com sinais de alarme
        ("12", 1, 1),   # dengue grave
        ("13", 0, 0),   # chikungunya
        ("12.0", 1, 1),
        (" 11 ", 1, 1),
    ],
)
def test_mapa_classi_fin(codigo, confirmado, grave):
    df = sinan_deng.preprocess(_fichas([codigo]))
    assert df["dengue_confirmado"].tolist() == [confirmado]
    assert df["dengue_grave"].tolist() == [grave]


def test_coorte_mantem_dengue_grave_e_tira_inconclusivo():
    # Regressão: o 12 (grave) saía da coorte e o 8 (inconclusivo) virava positivo.
    codigos = ["5", "8", "10", "11", "12", "13"]
    outcome = DengueGrave()
    coorte = outcome.build_cohort({"SINAN_DENG": _fichas(codigos)})
    assert len(coorte) == 3
    assert outcome.get_target(coorte).tolist() == [0, 1, 1]


def test_constantes_do_mapa():
    assert sinan_deng.CLASSI_CONFIRMADOS == {"10", "11", "12"}
    assert sinan_deng.CLASSI_POSITIVOS == {"11", "12"}
    assert sinan_deng.CLASSI_POSITIVOS <= sinan_deng.CLASSI_CONFIRMADOS
    assert set(sinan_deng.CLASSI_FIN) == {"5", "8", "10", "11", "12", "13"}
