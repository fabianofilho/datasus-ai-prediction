"""Dengue grave (sinais de alarme ou dengue grave) — SINAN-DENG."""

from __future__ import annotations

import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sinan_deng as deng_prep
from core.features import engineering as eng


class DengueGrave(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="dengue_grave",
            name="Dengue com Sinais de Alarme ou Grave",
            description=(
                "Prediz, a partir da notificação inicial de dengue, a probabilidade de evolução "
                "para dengue com sinais de alarme (CLASSI_FIN=8) ou dengue grave (CLASSI_FIN=11). "
                "Features incluem sintomas na notificação, idade, hospitalização e características "
                "demográficas. Utiliza dados do SINAN-Dengue."
            ),
            data_sources=["SINAN_DENG"],
            observation_window_days=0,
            prediction_window_days=14,
            requires_linkage=False,
            icon="🦟",
            estimated_download_min=8,
            suggested_features=[
                "idade_anos", "CS_SEXO", "CS_RACA", "CS_ESCOL_N",
                "FEBRE", "MIALGIA", "CEFALEIA", "EXANTEMA", "VOMITO",
                "NAUSEA", "DOR_COSTAS", "PETEQUIA_N", "LEUCOPENIA",
                "DOR_ABDOM", "VOMITO_2", "SANG_MUC", "VERTIG",
                "hospitalizado", "age_group",
            ],
            target_col="dengue_grave",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = deng_prep.preprocess(data["SINAN_DENG"])
        # Keep only confirmed dengue cases
        df = deng_prep.filter_confirmed(df)
        # Drop final classification columns to avoid leakage
        df = df.drop(columns=["CLASSI_FIN", "EVOLUCAO", "obito_dengue", "DT_OBITO"], errors="ignore")
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()

        if "idade_anos" in df.columns:
            df["age_group"] = eng.age_group(df["idade_anos"])
            df["idade_anos"] = pd.to_numeric(df["idade_anos"], errors="coerce")

        for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N"]:
            if col in df.columns:
                df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)

        df = eng.clip_outliers(df, "idade_anos")

        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
