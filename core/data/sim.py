"""SIM-DO (mortality declarations) preprocessor."""

from __future__ import annotations

import pandas as pd


KEEP_COLS = [
    "NUMERODO",
    "DTOBITO", "HORAOBITO",
    "DTNASC", "IDADE", "SEXO", "RACACOR",
    "CAUSABAS",                          # underlying cause (ICD-10)
    "LINHAA", "LINHAB", "LINHAC", "LINHAD",  # causal chain
    "CODMUNOCOR", "CODMUNRES",
    "LOCOCOR",                           # location of death
    # Identifiers
    "NOME", "NOMEMAE",
    "NUMERODOSN",                        # DNV link for neonatal/infant
    "CNS", "CPF",
]


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize a raw SIM DataFrame."""
    cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[cols].copy()

    # Dates
    for col in ["DTOBITO", "DTNASC"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", format="%d%m%Y")

    # Age in years (IDADE field uses a complex encoding)
    if "IDADE" in df.columns:
        df["idade_anos"] = _decode_idade(df["IDADE"])

    # Standardize identifiers
    for col in ["CNS", "CPF", "NOME", "NOMEMAE"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper().replace("NAN", "")

    return df


def _decode_idade(serie: pd.Series) -> pd.Series:
    """Decode SIM IDADE field to age in years.

    IDADE encoding:
      4XX → XX years
      3XX → XX months / 12
      2XX → XX days / 365
      1XX → XX hours / 8760
    """
    s = pd.to_numeric(serie, errors="coerce")
    unit = (s // 100).astype("Int64")
    value = (s % 100).astype(float)
    age = pd.Series(index=serie.index, dtype=float)
    age[unit == 4] = value[unit == 4]
    age[unit == 3] = value[unit == 3] / 12
    age[unit == 2] = value[unit == 2] / 365
    age[unit == 1] = value[unit == 1] / 8760
    return age
