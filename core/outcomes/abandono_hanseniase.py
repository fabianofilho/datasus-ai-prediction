"""Abandono de tratamento de hanseníase — SINAN-HANS."""

from __future__ import annotations

import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sinan_hans as hans_prep
from core.features import engineering as eng


class AbandonoHanseniase(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="abandono_hanseniase",
            name="Abandono de Tratamento — Hanseníase",
            description=(
                "Prediz o risco de abandono do tratamento de hanseníase (TPALTA_N=3). "
                "O tratamento padrão é 6 doses (PB) ou 12 doses (MB). "
                "Features incluem forma clínica, grau de incapacidade ao diagnóstico, "
                "modo de detecção, esquema terapêutico e características sociodemográficas. "
                "Utiliza dados do SINAN-Hanseníase."
            ),
            data_sources=["SINAN_HANS"],
            observation_window_days=0,
            prediction_window_days=365,
            requires_linkage=False,
            icon="💊",
            estimated_download_min=5,
            suggested_features=[
                "idade_anos", "CS_SEXO", "CS_RACA", "CS_ESCOL_N",
                "FORMACLINI", "mb", "grau_incapacidade",
                "MODOENTR", "MODODETECT", "BACILOSCOP",
                "ESQ_INI_N", "age_group",
            ],
            target_col="abandono",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = hans_prep.preprocess(data["SINAN_HANS"])
        df = hans_prep.filter_closed_cases(df)
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()

        if "idade_anos" in df.columns:
            df["age_group"] = eng.age_group(df["idade_anos"])
            df["idade_anos"] = pd.to_numeric(df["idade_anos"], errors="coerce")

        for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N",
                    "FORMACLINI", "MODOENTR", "MODODETECT",
                    "BACILOSCOP", "ESQ_INI_N"]:
            if col in df.columns:
                df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)

        for col in ["grau_incapacidade", "DOSE_RECEB"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = eng.clip_outliers(df, "idade_anos")

        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
