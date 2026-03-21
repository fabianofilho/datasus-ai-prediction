"""Abandono de tratamento de tuberculose — SINAN."""

from __future__ import annotations

import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sinan as sinan_prep
from core.features import engineering as eng


class AbandonoTB(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="abandono_tb",
            name="Abandono de Tratamento TB",
            description=(
                "Prediz o risco de abandono do tratamento de tuberculose (esquema padrão de 6 meses). "
                "Utiliza dados do SINAN (TB). O desfecho é EVOLUCAO=3 (abandono). "
                "Features incluem forma clínica, baciloscopia, co-infecção HIV, supervisão "
                "do tratamento (DOT), características sociodemográficas."
            ),
            data_sources=["SINAN_TB"],
            observation_window_days=0,
            prediction_window_days=180,
            requires_linkage=False,
            icon="💊",
            estimated_download_min=8,
            suggested_features=[
                "idade_anos", "CS_SEXO", "CS_RACA", "CS_ESCOL_N",
                "FORMA", "BACILOSC_E", "CULTURA_ES",
                "hiv_pos", "AGRAVAIDS",
                "dot", "TP_INFECC",
                "RAIOX_TORA",
                "age_group",
            ],
            target_col="abandono",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = sinan_prep.preprocess(data["SINAN_TB"])
        # Only cases with closure (definitive outcome known)
        df = sinan_prep.filter_closed_cases(df)
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()

        if "idade_anos" in df.columns:
            df["age_group"] = eng.age_group(df["idade_anos"])

        # Categoricals
        for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N", "FORMA",
                    "BACILOSC_E", "CULTURA_ES", "AGRAVAIDS",
                    "TP_INFECC", "RAIOX_TORA"]:
            if col in df.columns:
                df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)

        # Binary flags already created in preprocessor (dot, hiv_pos, abandono)
        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
