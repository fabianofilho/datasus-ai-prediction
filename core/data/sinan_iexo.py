"""SINAN-IEXO (intoxicação exógena) preprocessor."""
from __future__ import annotations
import pandas as pd

KEEP_COLS = [
    "NU_NOTIFIC", "DT_NOTIFIC", "DT_SIN_PRI", "DT_ENCERRA",
    "SG_UF_NOT", "ID_MUNICIP", "ID_MN_RESI",
    "NU_IDADE_N", "CS_SEXO", "CS_GESTANT", "CS_RACA", "CS_ESCOL_N",
    "ID_OCUPA_N",
    # Desfecho
    "CLASSI_FIN",       # 1=confirmado, 2=descartado, 3=inconclusivo, 8=outro, 9=ignorado
    "EVOLUCAO",         # 1=cura, 2=óbito agravo, 3=óbito outras, 4=sequela, 5=incapacidade, 9=ignorado
    "DT_OBITO",
    # Agente tóxico
    "AGENTE_TOX",       # categoria do agente
    "AGENTE_1", "AGENTE_2", "AGENTE_3",
    # Circunstância / intenção
    "CIRCUNSTAN",       # 1=acidental, 2=tentativa suicídio, 3=homicídio, 4=abuso, etc.
    "UTILIZACAO",
    # Via de exposição
    "VIA_1", "VIA_2", "VIA_3",
    # Atenção/local
    "TPATENDE",         # tipo de atendimento
    "HOSPITAL",         # hospitalizado
    # Trabalho
    "SIT_TRAB", "LOC_EXPO", "DOENCA_TRA",
]

# EVOLUCAO codes que representam desfecho adverso
EVOLUCAO_ADVERSO = {"2", "3", "4", "5"}  # óbito, sequela, incapacidade
CIRCUNSTAN_SUICIDIO = "2"


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in KEEP_COLS if c in df.columns]
    df = df[cols].copy()

    for col in ["DT_NOTIFIC", "DT_SIN_PRI", "DT_ENCERRA", "DT_OBITO"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "NU_IDADE_N" in df.columns:
        df["idade_anos"] = _decode_idade(df["NU_IDADE_N"])

    if "HOSPITAL" in df.columns:
        df["hospitalizado"] = (df["HOSPITAL"].astype(str).str.strip() == "1").astype(int)

    if "EVOLUCAO" in df.columns:
        evolucao = df["EVOLUCAO"].astype(str).str.strip()
        df["desfecho_adverso"] = evolucao.isin(EVOLUCAO_ADVERSO).astype(int)
        df["obito"] = evolucao.isin({"2", "3"}).astype(int)
        df["incapacidade"] = (evolucao == "5").astype(int)

    if "CIRCUNSTAN" in df.columns:
        df["tentativa_suicidio"] = (
            df["CIRCUNSTAN"].astype(str).str.strip() == CIRCUNSTAN_SUICIDIO
        ).astype(int)

    for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def filter_confirmed(df: pd.DataFrame) -> pd.DataFrame:
    if "CLASSI_FIN" in df.columns:
        return df[df["CLASSI_FIN"].astype(str).str.strip() == "1"].copy()
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
