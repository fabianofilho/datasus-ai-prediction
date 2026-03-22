"""SINAN-HANS (hanseniase / leprosy notifications) preprocessor."""

from __future__ import annotations

import pandas as pd


KEEP_COLS = [
    "TP_NOT",
    "DT_NOTIFIC", "DT_DIAG",
    "SG_UF_NOT", "ID_MUNICIP", "ID_MN_RESI",
    # Patient
    "NU_IDADE_N", "CS_SEXO", "CS_RACA", "CS_ESCOL_N", "CS_GESTANT",
    # Clinical
    "FORMACLINI",      # clinical form: 1=PB paucibacillar, 2=MB multibacillar
    "CLASSOPERA",      # operational classification
    "MODOENTR",        # entry mode: 1=new case, 2=transfer, etc.
    "MODODETECT",      # detection mode: 1=demand, 2=active, etc.
    "BACILOSCOP",      # baciloscopy: 0=neg, 1=pos, 2=not done
    "ESQ_INI_N",       # initial treatment scheme: 1=PB 6 doses, 2=MB 12 doses
    "AVALIA_N",        # disability evaluation at diagnosis: 0,1,2,9
    # Outcome
    "TPALTA_N",        # discharge type: 1=cure, 2=death, 3=abandonment, 4=transfer
    "DTALTA_N",        # discharge date
    # Treatment tracking
    "DOSE_RECEB",      # doses received
    "DTULTCOMP",       # last completion date
]

TPALTA_ABANDONO = "3"
TPALTA_CURA = "1"
TPALTA_OBITO = "2"


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize a raw SINAN-HANS DataFrame."""
    cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[cols].copy()

    # Dates
    for col in ["DT_NOTIFIC", "DT_DIAG", "DTALTA_N", "DTULTCOMP"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Age
    if "NU_IDADE_N" in df.columns:
        df["idade_anos"] = _decode_idade(df["NU_IDADE_N"])

    # Outcome flags
    if "TPALTA_N" in df.columns:
        alta = df["TPALTA_N"].astype(str).str.strip()
        df["abandono"] = (alta == TPALTA_ABANDONO).astype(int)
        df["cura"] = (alta == TPALTA_CURA).astype(int)

    # MB (multibacillar) flag — higher treatment burden
    if "FORMACLINI" in df.columns:
        df["mb"] = (df["FORMACLINI"].astype(str).str.strip() == "2").astype(int)

    # Disability at diagnosis
    if "AVALIA_N" in df.columns:
        df["grau_incapacidade"] = pd.to_numeric(df["AVALIA_N"], errors="coerce")

    # Standardize categoricals
    for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def filter_closed_cases(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only cases with a recorded discharge outcome."""
    if "TPALTA_N" in df.columns:
        closed = df["TPALTA_N"].astype(str).str.strip().isin(["1", "2", "3", "4", "5", "6"])
        return df[closed].copy()
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
