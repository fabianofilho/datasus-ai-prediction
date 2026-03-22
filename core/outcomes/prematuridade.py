"""Nascimento prematuro (<37 semanas) — SINASC."""

from __future__ import annotations

import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sinasc as sinasc_prep
from core.features import engineering as eng

# GESTACAO encoding: 1=<22w, 2=22-27w, 3=28-31w, 4=32-36w, 5=37-41w, 6=42+w
PRETERM_CODES = {"1", "2", "3", "4"}


class Prematuridade(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="prematuridade",
            name="Prematuridade",
            description=(
                "Prediz o risco de um nascimento ocorrer antes de 37 semanas de gestação "
                "(campo GESTACAO do SINASC: categorias 1 a 4). "
                "Features incluem características maternas, tipo de gravidez e parto, "
                "número de consultas pré-natais e apresentação fetal."
            ),
            data_sources=["SINASC"],
            observation_window_days=0,
            prediction_window_days=0,
            requires_linkage=False,
            icon="🤱",
            estimated_download_min=5,
            suggested_features=[
                "GRAVIDEZ", "PARTO", "CONSULTAS",
                "IDADEMAE", "ESCMAE", "RACACORMAE", "ESTCIVMAE",
                "SEXO", "TPAPRESENT", "STTRABPART", "STCESPARTO",
                "IDANOMAL", "age_group_mae",
            ],
            target_col="prematuro",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = sinasc_prep.preprocess(data["SINASC"])
        gestacao = df["GESTACAO"].astype(str) if "GESTACAO" in df.columns else pd.Series(dtype=str)
        df["prematuro"] = gestacao.isin(PRETERM_CODES).astype(int)
        # Remove GESTACAO and PESO to avoid leakage — target is derived from GESTACAO
        df = df.drop(columns=["GESTACAO", "preterm"], errors="ignore")
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()

        if "IDADEMAE" in df.columns:
            df["age_group_mae"] = eng.age_group(pd.to_numeric(df["IDADEMAE"], errors="coerce"))
            df["IDADEMAE"] = pd.to_numeric(df["IDADEMAE"], errors="coerce")

        for col in ["PARTO", "GRAVIDEZ", "TPAPRESENT", "SEXO",
                    "ESCMAE", "RACACORMAE", "ESTCIVMAE", "STTRABPART", "STCESPARTO"]:
            if col in df.columns:
                df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)

        if "CONSULTAS" in df.columns:
            df["CONSULTAS"] = pd.to_numeric(df["CONSULTAS"], errors="coerce")

        if "IDANOMAL" in df.columns:
            df["IDANOMAL"] = (df["IDANOMAL"].astype(str) == "1").astype(float)

        for col in ["PESO", "low_birth_weight", "very_low_birth_weight", "APGAR1", "APGAR5", "low_apgar5"]:
            df = df.drop(columns=[col], errors="ignore")

        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
