"""SINAN-VIOL (violência interpessoal/autoprovocada) preprocessor."""
from __future__ import annotations
import pandas as pd

KEEP_COLS = [
    "NU_NOTIFIC", "DT_NOTIFIC", "DT_OCOR", "DT_ENCERRA",
    "SG_UF_NOT", "ID_MUNICIP", "ID_MN_RESI",
    "NU_IDADE_N", "CS_SEXO", "CS_GESTANT", "CS_RACA", "CS_ESCOL_N",
    "SIT_CONJUG", "ORIENT_SEX", "IDENT_GEN", "CICL_VID",
    # Tipo de violência
    "VIOL_FISIC", "VIOL_PSICO", "VIOL_TORT", "VIOL_SEXU",
    "VIOL_TRAF", "VIOL_FINAN", "VIOL_NEGLI", "VIOL_INFAN",
    "VIOL_AUTO",   # autoprovocada (autoinfligida)
    # Agente
    "AG_FORCA", "AG_ENFOR", "AG_CORTE", "AG_QUENTE",
    "AG_ENVEN", "AG_FOGO", "AG_AMEACA",
    # Violência sexual
    "SEX_ASSEDI", "SEX_ESTUPR",
    # Agressor
    "REL_PAI", "REL_MAE", "REL_CONJ", "REL_EXCON", "REL_NAMO",
    "REL_POL", "AUTOR_SEXO", "AUTOR_DROGA",
    # Consequências
    "CONS_SUIC", "CONS_DST", "CONS_GRAV", "CONS_MENT",
    "CONS_COMP", "CONS_ESTRE",
    # Encaminhamentos
    "ENC_SAUDE", "ENC_TUTELA", "ENC_DEAM", "ENC_DELEG",
    "ENC_CREAS", "ENC_IML",
    # Local/circunstância
    "LOCAL_OCOR", "HORA_OCOR",
    # Repetição
    "VIOL_REPET",
]

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[cols].copy()

    for col in ["DT_NOTIFIC", "DT_OCOR", "DT_ENCERRA"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "NU_IDADE_N" in df.columns:
        df["idade_anos"] = _decode_idade(df["NU_IDADE_N"])

    bool_cols = [
        "VIOL_FISIC", "VIOL_PSICO", "VIOL_TORT", "VIOL_SEXU",
        "VIOL_TRAF", "VIOL_FINAN", "VIOL_NEGLI", "VIOL_INFAN", "VIOL_AUTO",
        "AG_FORCA", "AG_ENFOR", "AG_CORTE", "AG_QUENTE",
        "AG_ENVEN", "AG_FOGO", "AG_AMEACA",
        "SEX_ASSEDI", "SEX_ESTUPR",
        "REL_PAI", "REL_MAE", "REL_CONJ", "REL_EXCON", "REL_NAMO",
        "REL_POL", "AUTOR_DROGA",
        "CONS_SUIC", "CONS_DST", "CONS_GRAV", "CONS_MENT",
        "CONS_COMP", "CONS_ESTRE",
        "ENC_SAUDE", "ENC_TUTELA", "ENC_DEAM", "ENC_DELEG",
        "ENC_CREAS", "ENC_IML",
        "VIOL_REPET",
    ]
    for col in bool_cols:
        if col in df.columns:
            df[col] = (df[col].astype(str).str.strip() == "1").astype(int)

    # Target: consequência de suicídio ou violência autoprovocada
    suic = df.get("CONS_SUIC", pd.Series(0, index=df.index))
    auto = df.get("VIOL_AUTO", pd.Series(0, index=df.index))
    df["risco_autoprovocada"] = ((suic == 1) | (auto == 1)).astype(int)

    for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N", "ORIENT_SEX", "IDENT_GEN"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

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
