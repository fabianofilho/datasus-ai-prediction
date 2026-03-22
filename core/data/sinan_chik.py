"""SINAN-CHIK (chikungunya notifications) preprocessor."""
from __future__ import annotations
import pandas as pd

KEEP_COLS = [
    "NU_NOTIFIC", "DT_NOTIFIC", "DT_SIN_PRI", "DT_ENCERRA",
    "SG_UF_NOT", "ID_MUNICIP", "ID_MN_RESI",
    "NU_IDADE_N", "CS_SEXO", "CS_GESTANT", "CS_RACA", "CS_ESCOL_N",
    "CLASSI_FIN",       # 13=confirmado chik, 5=descartado
    "EVOLUCAO",         # 1=cura, 3=óbito, 9=ignorado
    "HOSPITALIZ",       # 1=sim, 2=não
    "DT_OBITO",
    # Sintomas
    "FEBRE", "MIALGIA", "CEFALEIA", "EXANTEMA", "VOMITO",
    "NAUSEA", "DOR_COSTAS", "ARTRITE", "ARTRALGIA", "CONJUNTVIT",
    "PETEQUIA_N", "LEUCOPENIA",
    # Comorbidades
    "DIABETES", "HEMATOLOG", "HEPATOPAT", "RENAL", "HIPERTENSA",
    "ACIDO_PEPT", "AUTO_IMUNE",
    # Sinais de alarme
    "ALRM_HIPOT", "ALRM_PLAQ", "ALRM_VOM", "ALRM_HEMAT",
    # Forma clínica
    "CLINC_CHIK",
]

CLASSI_CONFIRMADO = "13"
EVOLUCAO_OBITO = "3"


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[cols].copy()

    for col in ["DT_NOTIFIC", "DT_SIN_PRI", "DT_ENCERRA", "DT_OBITO"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "NU_IDADE_N" in df.columns:
        df["idade_anos"] = _decode_idade(df["NU_IDADE_N"])

    bool_cols = [
        "FEBRE", "MIALGIA", "CEFALEIA", "EXANTEMA", "VOMITO",
        "NAUSEA", "DOR_COSTAS", "ARTRITE", "ARTRALGIA", "CONJUNTVIT",
        "PETEQUIA_N", "LEUCOPENIA",
        "DIABETES", "HEMATOLOG", "HEPATOPAT", "RENAL", "HIPERTENSA",
        "ACIDO_PEPT", "AUTO_IMUNE",
        "ALRM_HIPOT", "ALRM_PLAQ", "ALRM_VOM", "ALRM_HEMAT",
    ]
    for col in bool_cols:
        if col in df.columns:
            df[col] = (df[col].astype(str).str.strip() == "1").astype(int)

    if "HOSPITALIZ" in df.columns:
        df["hospitalizado"] = (df["HOSPITALIZ"].astype(str).str.strip() == "1").astype(int)

    if "CLASSI_FIN" in df.columns:
        df["confirmado"] = (df["CLASSI_FIN"].astype(str).str.strip() == CLASSI_CONFIRMADO).astype(int)

    if "EVOLUCAO" in df.columns:
        df["obito"] = (df["EVOLUCAO"].astype(str).str.strip() == EVOLUCAO_OBITO).astype(int)

    for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def filter_confirmed(df: pd.DataFrame) -> pd.DataFrame:
    if "confirmado" in df.columns:
        return df[df["confirmado"] == 1].copy()
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
