"""SIH-RD (hospital admissions) preprocessor."""

from __future__ import annotations

import pandas as pd


# Columns we keep (subset of SIH-RD fields)
KEEP_COLS = [
    "N_AIH", "ANO_CMPT", "MES_CMPT",
    "NASC", "SEXO", "IDADE", "RACA_COR",
    "CEP", "MUNIC_RES", "MUNIC_MOV",
    "DT_INTER", "DT_SAIDA",
    "DIAG_PRINC", "DIAG_SECUN",     # primary + first secondary diagnosis
    "DIAGSEC1",                      # secondary diagnosis (newer layout)
    "PROC_SOLIC", "PROC_REA",
    "MORTE",                         # 0=alive, 1=in-hospital death (replaces MOT_SAIDA)
    "CAR_INT",
    "QT_DIARIAS", "DIAS_PERM",       # hospitalization days
    "VAL_TOT", "VAL_UTI",
    "UTI_MES_TO", "UTI_INT_TO",
    "CNES",
]


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize a raw SIH DataFrame."""
    cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[cols].copy()

    # Dates — stored as YYYYMMDD strings
    for col in ["DT_INTER", "DT_SAIDA"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", format="%Y%m%d")

    # Numeric
    for col in ["IDADE", "QT_DIARIAS", "DIAS_PERM", "VAL_TOT", "VAL_UTI", "UTI_MES_TO"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Length of stay
    if "DT_INTER" in df.columns and "DT_SAIDA" in df.columns:
        df["length_of_stay_days"] = (df["DT_SAIDA"] - df["DT_INTER"]).dt.days
    elif "DIAS_PERM" in df.columns:
        df["length_of_stay_days"] = pd.to_numeric(df["DIAS_PERM"], errors="coerce")

    # In-hospital death flag — MORTE is already 0/1 in the real SIH-RD data
    if "MORTE" in df.columns:
        df["is_death"] = pd.to_numeric(df["MORTE"], errors="coerce").fillna(0).astype(int)

    if "UTI_MES_TO" in df.columns:
        df["used_icu"] = (df["UTI_MES_TO"].fillna(0) > 0).astype(int)

    # Unify secondary diagnosis column name
    if "DIAGSEC1" in df.columns and "DIAG_SECUN" not in df.columns:
        df["DIAG_SEC"] = df["DIAGSEC1"]
    elif "DIAG_SECUN" in df.columns:
        df["DIAG_SEC"] = df["DIAG_SECUN"]

    # ICD-10 chapter
    if "DIAG_PRINC" in df.columns:
        df["diag_chapter"] = df["DIAG_PRINC"].astype(str).str[0]

    return df


def filter_alive_discharges(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only discharges where the patient left alive."""
    if "is_death" in df.columns:
        return df[df["is_death"] == 0].copy()
    return df
