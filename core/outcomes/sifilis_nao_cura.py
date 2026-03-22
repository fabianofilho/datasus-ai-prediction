"""Não-cura de sífilis adquirida — SINAN-SIFA."""
from __future__ import annotations
import pandas as pd
from core.outcomes.base import OutcomeConfig
from core.data import sinan_sifa as sifa_prep
from core.features import engineering as eng


class SifilisNaoCura(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="sifilis_nao_cura",
            name="Não-Cura de Sífilis Adquirida",
            description=(
                "Prediz o risco de um caso confirmado de sífilis adquirida não atingir cura "
                "(EVOLUCAO ≠ 1). O desfecho captura falha terapêutica, abandono ou óbito. "
                "Features incluem critério diagnóstico, doença tratada, "
                "idade, raça, escolaridade, sexo e tempo até diagnóstico. "
                "Utiliza SINAN-Sífilis Adquirida."
            ),
            data_sources=["SINAN_SIFA"],
            observation_window_days=0,
            prediction_window_days=180,
            requires_linkage=False,
            icon="🧫",
            estimated_download_min=5,
            suggested_features=[
                "idade_anos", "CS_SEXO", "CS_RACA", "CS_ESCOL_N",
                "CS_GESTANT", "CRITERIO", "DOENCA_TRA",
                "dias_notif_diag", "age_group",
            ],
            target_col="nao_cura",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = sifa_prep.preprocess(data["SINAN_SIFA"])
        df = sifa_prep.filter_confirmed(df)
        df = sifa_prep.filter_with_outcome(df)

        # Feature: dias entre notificação e diagnóstico
        if "DT_NOTIFIC" in df.columns and "DT_DIAG" in df.columns:
            df["dias_notif_diag"] = (
                pd.to_datetime(df["DT_DIAG"], errors="coerce")
                - pd.to_datetime(df["DT_NOTIFIC"], errors="coerce")
            ).dt.days

        df = df.drop(columns=["cura", "obito", "EVOLUCAO", "DT_OBITO"], errors="ignore")
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()
        if "idade_anos" in df.columns:
            df["age_group"] = eng.age_group(df["idade_anos"])
            df["idade_anos"] = pd.to_numeric(df["idade_anos"], errors="coerce")
        for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N", "CS_GESTANT", "CRITERIO", "DOENCA_TRA"]:
            if col in df.columns:
                df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)
        if "dias_notif_diag" in df.columns:
            df["dias_notif_diag"] = pd.to_numeric(df["dias_notif_diag"], errors="coerce")
            df = eng.clip_outliers(df, "dias_notif_diag")
        df = eng.clip_outliers(df, "idade_anos")
        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
