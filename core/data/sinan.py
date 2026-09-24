"""SINAN-TB (tuberculosis notifications) preprocessor."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


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
    "SITUA_ENCE",          # situação de encerramento: ver o mapa SITUA_ENCE abaixo
    "TP_INFECC",           # infection type (new/retreatment)
    "RAIOX_TORA",          # chest X-ray result
    # Identifiers
    "NM_PACIENT",
    "NM_MAE_PAC",
    "DT_NASC",
    "CNS_1",
    "TP_NOT",
]

# SITUA_ENCE (situação de encerramento) no dicionário vigente do SINAN-TB.
# Fonte: ENCERRAMENTO de sinan-continual-learning/core/diseases/tuberculose.py,
# coerente com core/features/data_dict.py e com o PySUS (5 = transferência,
# 7 = TB-DR). Não conferido contra um DBF real do TUBEBR. Os valores brutos
# podem vir com espaços ou como float ("2.0"), por isso são normalizados.
SITUA_ENCE = {
    "1": "cura",
    "2": "abandono",
    "3": "obito_tb",
    "4": "obito_outras_causas",
    "5": "transferencia",
    "6": "mudanca_diagnostico",
    "7": "tb_drogarresistente",
    "8": "mudanca_esquema",
    "9": "falencia",
    "10": "abandono_primario",
}
# Abandono (2) e abandono primário (10) são o desfecho positivo.
SITUA_ABANDONO = frozenset({"2", "10"})
# Censura: o desfecho do tratamento ficou desconhecido (o caso saiu de vista ou
# deixou de ser TB sensível). Sai da coorte de abandono e nunca vira 0.
SITUA_CENSURA = frozenset({"5", "6", "7", "8"})
SITUA_CURA = "1"
SITUA_OBITO = "3"      # óbito por TB (4 é óbito por outras causas)


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

    # Alvos binários a partir de SITUA_ENCE. abandono vale 1 em {2, 10}, 0 nos
    # demais encerramentos conhecidos (1, 3, 4, 9) e NaN na censura (5 a 8) ou
    # em código ausente/desconhecido: esses casos não têm desfecho de abandono.
    if "SITUA_ENCE" in df.columns:
        situacao = df["SITUA_ENCE"].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
        abandono = situacao.isin(SITUA_ABANDONO).astype(float)
        sem_desfecho = situacao.isin(SITUA_CENSURA) | ~situacao.isin(SITUA_ENCE.keys())
        df["abandono"] = abandono.mask(sem_desfecho, np.nan)
        df["cura"] = (situacao == SITUA_CURA).astype(int)

    # DOT (tratamento supervisionado)
    if "TRAT_SUPER" in df.columns:
        df["dot"] = (df["TRAT_SUPER"].astype(str).str.strip().str.replace(r'\.0$', '', regex=True) == "1").astype(int)

    # HIV positive flag
    if "HIV" in df.columns:
        df["hiv_pos"] = (df["HIV"].astype(str).str.strip().str.replace(r'\.0$', '', regex=True) == "1").astype(int)

    # Identifiers
    for col in ["NM_PACIENT", "NM_MAE_PAC", "CNS_1"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.replace(r'\.0$', '', regex=True).str.upper().replace("NAN", "")

    return df


def filter_closed_cases(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only cases with a definitive outcome (closure date present)."""
    if "DT_ENCERRA" in df.columns:
        return df[df["DT_ENCERRA"].notna()].copy()
    return df


def drop_censored(df: pd.DataFrame) -> pd.DataFrame:
    """Remove da coorte os casos sem desfecho de abandono (abandono NaN).

    São a censura (SITUA_ENCE 5 a 8) e os códigos ausentes ou fora do
    dicionário. A contagem por código vai para o log e para
    df.attrs["censura_abandono_tb"], para a exclusão ficar visível.
    """
    if "abandono" not in df.columns:
        return df
    sem_desfecho = df["abandono"].isna()
    n = int(sem_desfecho.sum())
    por_codigo: dict[str, int] = {}
    if n and "SITUA_ENCE" in df.columns:
        codigos = (
            df.loc[sem_desfecho, "SITUA_ENCE"].astype(str).str.strip()
            .str.replace(r'\.0$', '', regex=True)
        )
        por_codigo = {str(k): int(v) for k, v in codigos.value_counts().items()}
    out = df[~sem_desfecho].copy()
    out["abandono"] = out["abandono"].astype(int)
    out.attrs["censura_abandono_tb"] = {"n_excluidos": n, "por_codigo": por_codigo}
    if n:
        logger.warning(
            "abandono_tb: %d de %d casos excluídos da coorte por censura ou "
            "SITUA_ENCE desconhecido (por código: %s)",
            n, len(df), por_codigo,
        )
    return out


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
