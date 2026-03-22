"""SINAN-AIDS (HIV/AIDS notifications - adults) preprocessor."""
from __future__ import annotations
import pandas as pd

KEEP_COLS = [
    "NU_NOTIFIC", "DT_NOTIFIC", "DT_DIAG", "DT_CONFIRM",
    "SG_UF_NOT", "ID_MUNICIP", "ID_MN_RESI",
    "NU_IDADE_N", "CS_SEXO", "CS_GESTANT", "CS_RACA", "CS_ESCOL_N",
    "ID_OCUPA_N",
    # Desfecho
    "EVOLUCAO",         # 1=vivo, 2=óbito AIDS, 3=óbito outras, 9=ignorado
    "DT_OBITO",
    # Via de transmissão
    "ANT_TRASMI", "ANT_DROGA", "ANT_HEMOLF",
    # Doenças definidoras de AIDS
    "ANT_SARCOM", "ANT_TUBERC", "ANT_CANDID", "ANT_PULMON",
    "ANT_HERPES", "ANT_DISFUN", "ANT_DIARRE", "ANT_FEBRE",
    "ANT_CAQUEX", "ANT_TOXO", "ANT_PNEUMO", "ANT_CRIPTO",
    "ANT_LINFOM", "ANT_CHAGAS", "ANT_SALMO",
    # Diagnóstico
    "CRITERIO", "DEF_DIAGNO",
    "LAB_TRIAGE", "LAB_CONFIR",
]

EVOLUCAO_OBITO_AIDS = "2"
EVOLUCAO_VIVO = "1"


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[cols].copy()

    for col in ["DT_NOTIFIC", "DT_DIAG", "DT_CONFIRM", "DT_OBITO"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "NU_IDADE_N" in df.columns:
        df["idade_anos"] = _decode_idade(df["NU_IDADE_N"])

    if "EVOLUCAO" in df.columns:
        evolucao = df["EVOLUCAO"].astype(str).str.strip()
        df["obito_aids"] = (evolucao == EVOLUCAO_OBITO_AIDS).astype(int)
        df["vivo"] = (evolucao == EVOLUCAO_VIVO).astype(int)

    # AIDS-defining disease count
    ad_cols = [c for c in ["ANT_SARCOM", "ANT_TUBERC", "ANT_CANDID", "ANT_PULMON",
                            "ANT_HERPES", "ANT_DISFUN", "ANT_DIARRE", "ANT_FEBRE",
                            "ANT_CAQUEX", "ANT_TOXO", "ANT_PNEUMO", "ANT_CRIPTO",
                            "ANT_LINFOM", "ANT_CHAGAS", "ANT_SALMO"] if c in df.columns]
    if ad_cols:
        for c in ad_cols:
            df[c] = (df[c].astype(str).str.strip() == "1").astype(int)
        df["n_doencas_aids"] = df[ad_cols].sum(axis=1)

    bool_cols = ["ANT_TRASMI", "ANT_DROGA", "ANT_HEMOLF"]
    for col in bool_cols:
        if col in df.columns:
            df[col] = (df[col].astype(str).str.strip() == "1").astype(int)

    for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def filter_with_outcome(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only cases with a known outcome (non-empty EVOLUCAO)."""
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
