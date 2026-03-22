"""SINAN-DENG (dengue notifications) preprocessor."""

from __future__ import annotations

import pandas as pd


KEEP_COLS = [
    "NU_NOTIFIC",
    "DT_NOTIFIC", "DT_SIN_PRI", "DT_DIGITA", "DT_ENCERRA",
    "SG_UF_NOT", "ID_MUNICIP",
    # Patient
    "NU_IDADE_N", "CS_SEXO", "CS_RACA", "CS_ESCOL_N",
    "ID_MN_RESI",
    # Clinical
    "CLASSI_FIN",      # final classification: 10=dengue, 8=c/ sinais alarme, 11=grave, 12=descartado
    "EVOLUCAO",        # 1=cure, 2=death by dengue, 3=death other, 9=unknown
    "HOSPITALIZ",      # hospitalized: 1=yes, 2=no
    "DT_OBITO",
    # Signs/symptoms (selected)
    "FEBRE", "MIALGIA", "CEFALEIA", "EXANTEMA", "VOMITO",
    "NAUSEA", "DOR_COSTAS", "CONJUNTVIT", "ARTRITE",
    # Warning signs
    "PETEQUIA_N", "LEUCOPENIA", "DOR_ABDOM", "VOMITO_2",
    "SANG_MUC", "VERTIG", "PRESSAO",
    # Severe dengue
    "CHOQUE", "CONVULSAO", "HEPATOPAT", "INSUF_RESP",
]

# CLASSI_FIN codes
CLASSI_DENGUE = "10"
CLASSI_ALARME = "8"
CLASSI_GRAVE = "11"

# EVOLUCAO codes
EVOLUCAO_OBITO_DENGUE = "2"


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize a raw SINAN-DENGUE DataFrame."""
    cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[cols].copy()

    # Dates
    for col in ["DT_NOTIFIC", "DT_SIN_PRI", "DT_ENCERRA", "DT_OBITO"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Age
    if "NU_IDADE_N" in df.columns:
        df["idade_anos"] = _decode_idade(df["NU_IDADE_N"])

    # Binary flags for warning signs and severe dengue features
    bool_cols = [
        "FEBRE", "MIALGIA", "CEFALEIA", "EXANTEMA", "VOMITO",
        "NAUSEA", "DOR_COSTAS", "CONJUNTVIT", "ARTRITE",
        "PETEQUIA_N", "LEUCOPENIA", "DOR_ABDOM", "VOMITO_2",
        "SANG_MUC", "VERTIG", "PRESSAO",
        "CHOQUE", "CONVULSAO", "HEPATOPAT", "INSUF_RESP",
    ]
    for col in bool_cols:
        if col in df.columns:
            df[col] = (df[col].astype(str).str.strip() == "1").astype(int)

    # Hospitalization flag
    if "HOSPITALIZ" in df.columns:
        df["hospitalizado"] = (df["HOSPITALIZ"].astype(str).str.strip() == "1").astype(int)

    # Target derivations
    if "CLASSI_FIN" in df.columns:
        classi = df["CLASSI_FIN"].astype(str).str.strip()
        df["dengue_grave"] = classi.isin([CLASSI_ALARME, CLASSI_GRAVE]).astype(int)
        df["dengue_confirmado"] = classi.isin([CLASSI_DENGUE, CLASSI_ALARME, CLASSI_GRAVE]).astype(int)

    if "EVOLUCAO" in df.columns:
        evolucao = df["EVOLUCAO"].astype(str).str.strip()
        df["obito_dengue"] = (evolucao == EVOLUCAO_OBITO_DENGUE).astype(int)

    # Identifiers
    if "CS_SEXO" in df.columns:
        df["CS_SEXO"] = df["CS_SEXO"].astype(str).str.strip()

    return df


def filter_confirmed(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only confirmed dengue cases."""
    if "dengue_confirmado" in df.columns:
        return df[df["dengue_confirmado"] == 1].copy()
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
