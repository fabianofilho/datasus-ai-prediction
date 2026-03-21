"""Mortalidade neonatal — SINASC + SIM."""

from __future__ import annotations

import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sinasc as sinasc_prep, sim as sim_prep
from core.data.linker import link_sinasc_sim
from core.features import engineering as eng


class MortalidadeNeonatal(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="mortalidade_neonatal",
            name="Mortalidade Neonatal",
            description=(
                "Prediz o risco de óbito nos primeiros 28 dias de vida a partir das "
                "características do nascimento (SINASC) e record linkage com o SIM. "
                "Features incluem peso ao nascer, Apgar, idade gestacional, tipo de parto, "
                "consultas pré-natais e características maternas."
            ),
            data_sources=["SINASC", "SIM"],
            observation_window_days=0,
            prediction_window_days=28,
            requires_linkage=True,
            icon="👶",
            estimated_download_min=12,
            suggested_features=[
                "PESO", "APGAR1", "APGAR5", "GESTACAO",
                "PARTO", "CONSULTAS", "IDADEMAE",
                "SEXO", "GRAVIDEZ", "TPAPRESENT",
                "IDANOMAL", "low_birth_weight", "very_low_birth_weight",
                "low_apgar5", "preterm",
                "ESCMAE", "RACACORMAE", "ESTCIVMAE",
            ],
            target_col="neonatal_death",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        sinasc = sinasc_prep.preprocess(data["SINASC"])

        if "SIM" in data and data["SIM"] is not None:
            sim = sim_prep.preprocess(data["SIM"])
            df = link_sinasc_sim(sinasc, sim, window_days=self.prediction_window_days)
        else:
            sinasc["neonatal_death"] = 0
            df = sinasc

        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()

        # Numerics
        for col in ["PESO", "APGAR1", "APGAR5", "CONSULTAS", "IDADEMAE"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Clip outliers
        df = eng.clip_outliers(df, "PESO", 0.005, 0.995)
        df = eng.clip_outliers(df, "IDADEMAE")

        # Categoricals → numeric codes
        for col in ["GESTACAO", "PARTO", "GRAVIDEZ", "TPAPRESENT", "SEXO",
                    "ESCMAE", "RACACORMAE", "ESTCIVMAE"]:
            if col in df.columns:
                df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)

        # Anomaly flag
        if "IDANOMAL" in df.columns:
            df["IDANOMAL"] = (df["IDANOMAL"].astype(str) == "1").astype(float)

        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
