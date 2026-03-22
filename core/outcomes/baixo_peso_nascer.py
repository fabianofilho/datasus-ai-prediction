"""Baixo peso ao nascer (<2500g) — SINASC."""

from __future__ import annotations

import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sinasc as sinasc_prep
from core.features import engineering as eng

THRESHOLD_GRAMS = 2500


class BaixoPesoNascer(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="baixo_peso_nascer",
            name="Baixo Peso ao Nascer",
            description=(
                f"Prediz a probabilidade de um recém-nascido ter peso inferior a "
                f"{THRESHOLD_GRAMS}g. Utiliza apenas dados disponíveis no momento do "
                "nascimento (SINASC): características maternas, tipo de parto, "
                "gestação múltipla e número de consultas pré-natais."
            ),
            data_sources=["SINASC"],
            observation_window_days=0,
            prediction_window_days=0,
            requires_linkage=False,
            icon="⚖️",
            estimated_download_min=5,
            suggested_features=[
                "GESTACAO", "GRAVIDEZ", "PARTO", "CONSULTAS",
                "IDADEMAE", "ESCMAE", "RACACORMAE", "ESTCIVMAE",
                "SEXO", "TPAPRESENT", "STTRABPART", "STCESPARTO",
                "preterm", "age_group_mae",
            ],
            target_col="baixo_peso",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = sinasc_prep.preprocess(data["SINASC"])
        peso = pd.to_numeric(df["PESO"], errors="coerce") if "PESO" in df.columns else pd.Series(dtype=float)
        df["baixo_peso"] = (peso < THRESHOLD_GRAMS).astype(int)
        # Remove PESO from features to avoid leakage
        df = df.drop(columns=["PESO", "low_birth_weight", "very_low_birth_weight"], errors="ignore")
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

        if "CONSULTAS" in df.columns:
            df["CONSULTAS"] = pd.to_numeric(df["CONSULTAS"], errors="coerce")

        if "IDANOMAL" in df.columns:
            df["IDANOMAL"] = (df["IDANOMAL"].astype(str) == "1").astype(float)

        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
