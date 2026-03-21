"""SINASC-DN (live births) preprocessor."""

from __future__ import annotations

import pandas as pd


KEEP_COLS = [
    "NUMERODN",
    "DTNASC",
    "SEXO", "PESO",
    "APGAR1", "APGAR5",
    "GESTACAO",          # gestational age (weeks category)
    "GRAVIDEZ",          # single/twin/triplet
    "PARTO",             # delivery type (vaginal/cesarean)
    "CONSULTAS",         # prenatal visits count
    "IDADEMAE",
    "ESCMAE",            # maternal education
    "RACACORMAE", "RACACOR",
    "ESTCIVMAE",
    "CODANOMAL",         # congenital anomaly ICD-10
    "IDANOMAL",          # anomaly flag
    "TPAPRESENT",        # fetal presentation
    "STTRABPART",        # labor induction
    "STCESPARTO",        # planned cesarean flag
    "CODMUNRES", "CODMUNNASC",
    "CNES",              # facility
    # Identifiers
    "NOMEMAE",
    "DTNASC",
    "CNS_MAE", "CPF_MAE",
    "CNS",               # infant CNS
]


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize a raw SINASC DataFrame."""
    cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[cols].copy()

    # Date
    if "DTNASC" in df.columns:
        df["DTNASC"] = pd.to_datetime(df["DTNASC"], errors="coerce", format="%d%m%Y")

    # Numeric
    for col in ["PESO", "APGAR1", "APGAR5", "IDADEMAE", "CONSULTAS"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Derived risk flags
    if "PESO" in df.columns:
        df["low_birth_weight"] = (df["PESO"] < 2500).astype(int)
        df["very_low_birth_weight"] = (df["PESO"] < 1500).astype(int)

    if "APGAR5" in df.columns:
        df["low_apgar5"] = (pd.to_numeric(df["APGAR5"], errors="coerce") < 7).astype(int)

    if "GESTACAO" in df.columns:
        # GESTACAO: 1=<22w, 2=22-27, 3=28-31, 4=32-36, 5=37-41, 6=42+
        df["preterm"] = df["GESTACAO"].astype(str).isin(["1", "2", "3", "4"]).astype(int)

    # Identifiers
    for col in ["CNS_MAE", "CPF_MAE", "CNS", "NOMEMAE"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper().replace("NAN", "")

    return df
