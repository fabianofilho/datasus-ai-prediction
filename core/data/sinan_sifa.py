"""SINAN-SIFA (sífilis adquirida) preprocessor."""
from __future__ import annotations
import pandas as pd

KEEP_COLS = [
    "NU_NOTIFIC", "DT_NOTIFIC", "DT_DIAG", "DT_INVEST", "DT_ENCERRA",
    "SG_UF_NOT", "ID_MUNICIP", "ID_MN_RESI",
    "NU_IDADE_N", "CS_SEXO", "CS_GESTANT", "CS_RACA", "CS_ESCOL_N",
    "ID_OCUPA_N",
    # Desfecho
    "CLASSI_FIN",       # 1=confirmado, 8=descartado
    "EVOLUCAO",         # 1=cura, 2=?? , 3=óbito, 9=ignorado
    "DT_OBITO",
    # Diagnóstico
    "CRITERIO",         # critério diagnóstico
    "DOENCA_TRA",       # doença tratada
]

EVOLUCAO_CURA = "1"
EVOLUCAO_ADVERSO = {"2", "3", "9"}  # inclui ignorado como não-cura para ML


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[cols].copy()

    for col in ["DT_NOTIFIC", "DT_DIAG", "DT_INVEST", "DT_ENCERRA", "DT_OBITO"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "NU_IDADE_N" in df.columns:
        df["idade_anos"] = _decode_idade(df["NU_IDADE_N"])

    if "EVOLUCAO" in df.columns:
        evolucao = df["EVOLUCAO"].astype(str).str.strip()
        df["cura"] = (evolucao == EVOLUCAO_CURA).astype(int)
        # nao_cura: confirmed non-cure (excludes blank/ignored)
        df["nao_cura"] = evolucao.isin({"2", "3"}).astype(int)
        df["obito"] = (evolucao == "3").astype(int)

    for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def filter_confirmed(df: pd.DataFrame) -> pd.DataFrame:
    if "CLASSI_FIN" in df.columns:
        return df[df["CLASSI_FIN"].astype(str).str.strip() == "1"].copy()
    return df


def filter_with_outcome(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only cases with a known cure/non-cure outcome."""
    if "EVOLUCAO" in df.columns:
        known = df["EVOLUCAO"].astype(str).str.strip().isin(["1", "2", "3"])
        return df[known].copy()
    return df


def _decode_idade(serie: pd.Series) -> pd.Series:
    s = pd.to_numeric(serie, errors="coerce")
    unit = (s // 1000).astype("Int64")
    value = (s % 1000).astype(float)
    age = pd.Series(index=serie.index, dtype=float)
    age[unit == 4] = value[unit == 4]
    age[unit == 3] = value[unit == 3] / 12
    age[unit == 2] = value[unit == 2] / 365
    age[unit == 1] = value[unit == 1] / 8760
    return age
