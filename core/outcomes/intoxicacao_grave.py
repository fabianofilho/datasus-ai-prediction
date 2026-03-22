"""Desfecho adverso em intoxicação exógena — SINAN-IEXO."""
from __future__ import annotations
import pandas as pd
from core.outcomes.base import OutcomeConfig
from core.data import sinan_iexo as iexo_prep
from core.features import engineering as eng


class IntoxicacaoGrave(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="intoxicacao_grave",
            name="Desfecho Adverso em Intoxicação Exógena",
            description=(
                "Prediz a probabilidade de um caso de intoxicação exógena resultar em "
                "desfecho adverso: óbito (EVOLUCAO=2 ou 3) ou incapacidade permanente (EVOLUCAO=5). "
                "Features incluem agente tóxico, circunstância (acidental vs. tentativa de suicídio), "
                "via de exposição, hospitalização e características demográficas. "
                "Utiliza SINAN-Intoxicação Exógena."
            ),
            data_sources=["SINAN_IEXO"],
            observation_window_days=0,
            prediction_window_days=30,
            requires_linkage=False,
            icon="☠️",
            estimated_download_min=8,
            suggested_features=[
                "idade_anos", "CS_SEXO", "CS_RACA", "CS_ESCOL_N",
                "AGENTE_TOX", "AGENTE_1", "CIRCUNSTAN",
                "VIA_1", "TPATENDE", "hospitalizado",
                "tentativa_suicidio", "SIT_TRAB", "CS_GESTANT",
                "age_group",
            ],
            target_col="desfecho_adverso",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = iexo_prep.preprocess(data["SINAN_IEXO"])
        df = iexo_prep.filter_confirmed(df)
        # Manter apenas casos com desfecho conhecido
        if "EVOLUCAO" in data["SINAN_IEXO"].columns:
            known = data["SINAN_IEXO"]["EVOLUCAO"].astype(str).str.strip().isin(
                ["1", "2", "3", "4", "5"]
            )
            df = df[known.values[:len(df)]].copy() if len(known) == len(df) else df
        df = df.drop(columns=["obito", "incapacidade", "EVOLUCAO", "DT_OBITO"], errors="ignore")
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()
        if "idade_anos" in df.columns:
            df["age_group"] = eng.age_group(df["idade_anos"])
            df["idade_anos"] = pd.to_numeric(df["idade_anos"], errors="coerce")
        for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N", "CS_GESTANT",
                    "AGENTE_TOX", "AGENTE_1", "CIRCUNSTAN", "VIA_1", "TPATENDE", "SIT_TRAB"]:
            if col in df.columns:
                df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)
        df = eng.clip_outliers(df, "idade_anos")
        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
