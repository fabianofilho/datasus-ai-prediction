"""Flag multibacilar da hanseníase (PRED-03).

mb vem da classificação operacional: CLASSOPERA 1 = PB, 2 = MB. FORMACLINI é
a forma clínica (2 = tuberculoide, paucibacilar) e não define mb.
"""

from __future__ import annotations

import pandas as pd
import pytest

from core.data import sinan_hans


@pytest.mark.parametrize(
    "classopera, esperado",
    [("1", 0), ("2", 1), ("2.0", 1), (" 2 ", 1), (2, 1), ("9", 0), ("", 0), (None, 0)],
)
def test_mb_vem_de_classopera(classopera, esperado):
    df = sinan_hans.preprocess(pd.DataFrame({"CLASSOPERA": [classopera]}))
    assert df["mb"].tolist() == [esperado]


def test_forma_clinica_nao_define_mb():
    # Regressão: FORMACLINI 2 (tuberculoide) marcava mb = 1.
    df = sinan_hans.preprocess(pd.DataFrame({
        "FORMACLINI": ["1", "2", "3", "4"],
        "CLASSOPERA": ["1", "1", "2", "2"],
    }))
    assert df["mb"].tolist() == [0, 0, 1, 1]


def test_sem_classopera_nao_cria_mb():
    df = sinan_hans.preprocess(pd.DataFrame({"FORMACLINI": ["2", "3"]}))
    assert "mb" not in df.columns
