"""Apgar baixo no 5º minuto (<7) — SINASC."""

from __future__ import annotations

import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sinasc as sinasc_prep
from core.features import engineering as eng


class ApgarBaixo(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="apgar_baixo",
            name="Apgar Baixo no 5º Minuto",
            description=(
                "Prediz a probabilidade de um recém-nascido apresentar índice de Apgar "
                "inferior a 7 no quinto minuto de vida (APGAR5 < 7), indicador de "
                "asfixia neonatal. Features incluem peso, idade gestacional, tipo de parto, "
                "apresentação fetal e características maternas."
            ),
            data_sources=["SINASC"],
            observation_window_days=0,
            prediction_window_days=0,
            requires_linkage=False,
            icon="🩺",
            estimated_download_min=5,
            suggested_features=[
                "PESO", "GESTACAO", "PARTO", "GRAVIDEZ",
                "TPAPRESENT", "STTRABPART", "STCESPARTO",
                "IDADEMAE", "ESCMAE", "RACACORMAE",
                "SEXO", "IDANOMAL", "CONSULTAS",
                "low_birth_weight", "preterm", "age_group_mae",
            ],
            target_col="apgar_baixo_5min",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = sinasc_prep.preprocess(data["SINASC"])
        apgar5 = pd.to_numeric(df["APGAR5"], errors="coerce") if "APGAR5" in df.columns else pd.Series(dtype=float)
        df["apgar_baixo_5min"] = (apgar5 < 7).astype(int)
        # Remove APGAR columns to avoid leakage
        df = df.drop(columns=["APGAR1", "APGAR5", "low_apgar5"], errors="ignore")
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()

        if "IDADEMAE" in df.columns:
            df["age_group_mae"] = eng.age_group(pd.to_numeric(df["IDADEMAE"], errors="coerce"))
            df["IDADEMAE"] = pd.to_numeric(df["IDADEMAE"], errors="coerce")

        for col in ["GESTACAO", "PARTO", "GRAVIDEZ", "TPAPRESENT", "SEXO",
                    "ESCMAE", "RACACORMAE", "ESTCIVMAE", "STTRABPART", "STCESPARTO"]:
            if col in df.columns:
                df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)

        for col in ["PESO", "CONSULTAS"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "IDANOMAL" in df.columns:
            df["IDANOMAL"] = (df["IDANOMAL"].astype(str) == "1").astype(float)

        df = eng.clip_outliers(df, "PESO")

        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
