"""SINAN-TB (tuberculosis notifications) preprocessor."""

from __future__ import annotations

import pandas as pd


KEEP_COLS = [
    "NU_NOTIFIC",          # notification number
    "DT_NOTIFIC",          # notification date
    "DT_DIAG",             # diagnosis date
    "DT_ENCERRA",          # case closure date
    "SEM_NOT",             # epidemiological week
    # Patient
    "NU_IDADE_N",          # age
    "CS_SEXO",
    "CS_RACA",
    "CS_ESCOL_N",          # education
    "ID_MN_RESI",          # municipality of residence
    "SG_UF_NOT",           # state of notification
    # Clinical
    "FORMA",               # clinical form (pulmonary/extrapulmonary/both)
    "BACILOSC_E",          # initial sputum smear
    "CULTURA_ES",          # sputum culture
    "HIV",                 # HIV co-infection status
    "AGRAVAIDS",           # AIDS complication
    "TRAT_SUPER",          # directly observed treatment (DOT)
    "SITUA_ENCE",          # case closure situation: 1=cure,2=death,3=abandon,5=transfer
    "TP_INFECC",           # infection type (new/retreatment)
    "RAIOX_TORA",          # chest X-ray result
    # Identifiers
    "NM_PACIENT",
    "NM_MAE_PAC",
    "DT_NASC",
    "CNS_1",
    "TP_NOT",
]

# SITUA_ENCE codes (values may have leading/trailing spaces in raw data)
SITUA_ABANDONO = "3"   # treatment abandonment
SITUA_CURA = "1"       # cure
SITUA_OBITO = "2"      # death


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize a raw SINAN-TB DataFrame."""
    cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[cols].copy()

    # Dates — dbfread already returns date objects; coerce gracefully
    for col in ["DT_NOTIFIC", "DT_DIAG", "DT_ENCERRA", "DT_NASC"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Age in years
    if "NU_IDADE_N" in df.columns:
        df["idade_anos"] = _decode_idade_sinan(df["NU_IDADE_N"])

    # Binary target helpers — strip spaces from SITUA_ENCE values
    if "SITUA_ENCE" in df.columns:
        situacao = df["SITUA_ENCE"].astype(str).str.strip()
        df["abandono"] = (situacao == SITUA_ABANDONO).astype(int)
        df["cura"] = (situacao == SITUA_CURA).astype(int)

    # DOT (tratamento supervisionado)
    if "TRAT_SUPER" in df.columns:
        df["dot"] = (df["TRAT_SUPER"].astype(str).str.strip() == "1").astype(int)

    # HIV positive flag
    if "HIV" in df.columns:
        df["hiv_pos"] = (df["HIV"].astype(str).str.strip() == "1").astype(int)

    # Identifiers
    for col in ["NM_PACIENT", "NM_MAE_PAC", "CNS_1"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper().replace("NAN", "")

    return df


def filter_closed_cases(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only cases with a definitive outcome (closure date present)."""
    if "DT_ENCERRA" in df.columns:
        return df[df["DT_ENCERRA"].notna()].copy()
    return df


def _decode_idade_sinan(serie: pd.Series) -> pd.Series:
    """Decode SINAN NU_IDADE_N to years (similar logic to SIM IDADE)."""
    s = pd.to_numeric(serie, errors="coerce")
    unit = (s // 1000).astype("Int64")
    value = (s % 1000).astype(float)
    age = pd.Series(index=serie.index, dtype=float)
    age[unit == 4] = value[unit == 4]         # years
    age[unit == 3] = value[unit == 3] / 12    # months
    age[unit == 2] = value[unit == 2] / 365   # days
    age[unit == 1] = value[unit == 1] / 8760  # hours
    return age
