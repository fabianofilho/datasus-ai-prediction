"""Hospitalização por chikungunya — SINAN-CHIK."""
from __future__ import annotations
import pandas as pd
from core.outcomes.base import OutcomeConfig
from core.data import sinan_chik as chik_prep
from core.features import engineering as eng


class ChikungunyaHospitalizado(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="chikungunya_hospitalizado",
            name="Hospitalização por Chikungunya",
            description=(
                "Prediz a probabilidade de um paciente notificado com chikungunya necessitar "
                "de hospitalização. Features incluem sintomas na notificação inicial, "
                "comorbidades (diabetes, hipertensão, doença renal, hepatopatia), "
                "sinais de alarme e características demográficas. Utiliza SINAN-Chikungunya."
            ),
            data_sources=["SINAN_CHIK"],
            observation_window_days=0,
            prediction_window_days=14,
            requires_linkage=False,
            icon="🦟",
            estimated_download_min=6,
            suggested_features=[
                "idade_anos", "CS_SEXO", "CS_RACA", "CS_ESCOL_N",
                "FEBRE", "MIALGIA", "ARTRITE", "ARTRALGIA", "VOMITO",
                "PETEQUIA_N", "LEUCOPENIA",
                "DIABETES", "HIPERTENSA", "RENAL", "HEPATOPAT",
                "ALRM_HIPOT", "ALRM_PLAQ", "ALRM_VOM",
                "CS_GESTANT", "age_group",
            ],
            target_col="hospitalizado",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = chik_prep.preprocess(data["SINAN_CHIK"])
        df = chik_prep.filter_confirmed(df)
        df = df.drop(columns=["obito", "EVOLUCAO", "DT_OBITO", "CLINC_CHIK"], errors="ignore")
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()
        if "idade_anos" in df.columns:
            df["age_group"] = eng.age_group(df["idade_anos"])
            df["idade_anos"] = pd.to_numeric(df["idade_anos"], errors="coerce")
        for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N", "CS_GESTANT"]:
            if col in df.columns:
                df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)
        df = eng.clip_outliers(df, "idade_anos")
        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
