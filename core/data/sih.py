"""SIH-RD (hospital admissions) preprocessor."""

from __future__ import annotations

import pandas as pd


# Columns we keep (subset of SIH-RD fields)
KEEP_COLS = [
    "N_AIH", "ANO_CMPT", "MES_CMPT",
    "NASC", "SEXO", "IDADE", "RACA_COR",
    "CEP", "MUNIC_RES", "MUNIC_MOV",
    "DT_INTER", "DT_SAIDA",
    "DIAG_PRINC", "DIAG_SEC",
    "PROC_SOLIC", "PROC_REA",
    "MOT_SAIDA", "CAR_INT",
    "DIARIAS", "VAL_TOT", "VAL_UTI",
    "UTI_MES_TO", "UTI_INT_TO",
    "CNES",
    # Identifiers for record linkage
    "CNS_PAC", "CPF_PAC",
]

# MOT_SAIDA codes that indicate in-hospital death
DEATH_MOTIVOS = {"5", "6", "7"}


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize a raw SIH DataFrame.

    Returns a DataFrame with standardized types, parsed dates,
    and derived helper columns (is_death, length_of_stay_days).
    """
    # Keep only available columns
    cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[cols].copy()

    # Dates
    for col in ["DT_INTER", "DT_SAIDA"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", format="%Y%m%d")

    # Numeric
    for col in ["IDADE", "DIARIAS", "VAL_TOT", "VAL_UTI", "UTI_MES_TO"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Derived
    if "DT_INTER" in df.columns and "DT_SAIDA" in df.columns:
        df["length_of_stay_days"] = (df["DT_SAIDA"] - df["DT_INTER"]).dt.days

    if "MOT_SAIDA" in df.columns:
        df["is_death"] = df["MOT_SAIDA"].astype(str).isin(DEATH_MOTIVOS).astype(int)

    if "UTI_MES_TO" in df.columns:
        df["used_icu"] = (df["UTI_MES_TO"].fillna(0) > 0).astype(int)

    # Standardize identifiers
    for col in ["CNS_PAC", "CPF_PAC"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace("nan", "")

    # ICD-10 prefix (chapter) as a categorical feature
    if "DIAG_PRINC" in df.columns:
        df["diag_chapter"] = df["DIAG_PRINC"].astype(str).str[0]

    return df


def filter_alive_discharges(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only discharges where the patient left alive (non-death MOT_SAIDA)."""
    if "is_death" in df.columns:
        return df[df["is_death"] == 0].copy()
    return df
