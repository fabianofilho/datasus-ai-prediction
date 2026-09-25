"""Upload manual de CSV (PRED-16).

load_from_csv passava low_memory=False junto com engine="python", combinação
que o pandas rejeita: toda leitura lançava ValueError.
"""

from __future__ import annotations

import pandas as pd
import pytest

from core.data import downloader


@pytest.fixture
def raw_dir_temporario(tmp_path, monkeypatch):
    # Não grava no cache real (data/raw ou /tmp/datasus_raw).
    monkeypatch.setattr(downloader, "RAW_DIR", tmp_path)
    return tmp_path


@pytest.mark.parametrize("sep", [",", ";"])
def test_load_from_csv_le_csv_pequeno(raw_dir_temporario, sep):
    linhas = [
        sep.join(["SITUA_ENCE", "CS_SEXO", "NM_MUNIC"]),
        sep.join(["2", "F", "São Paulo"]),
        sep.join(["1", "M", "Açailândia"]),
        sep.join(["10", "F", "Belém"]),
    ]
    csv_bytes = ("\n".join(linhas) + "\n").encode("latin-1")

    df = downloader.load_from_csv(csv_bytes, "SINAN_TB", "SP", 2023)

    assert list(df.columns) == ["SITUA_ENCE", "CS_SEXO", "NM_MUNIC"]
    assert len(df) == 3
    assert df["NM_MUNIC"].tolist() == ["São Paulo", "Açailândia", "Belém"]
    assert df["SITUA_ENCE"].tolist() == [2, 1, 10]

    cache = raw_dir_temporario / "sinan_tb_SP_2023.parquet"
    assert cache.exists()
    pd.testing.assert_frame_equal(pd.read_parquet(cache), df)
