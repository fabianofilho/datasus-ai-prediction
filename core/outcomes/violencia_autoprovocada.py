"""Risco de violência autoprovocada/suicídio — SINAN-VIOL."""
from __future__ import annotations
import pandas as pd
from core.outcomes.base import OutcomeConfig
from core.data import sinan_viol as viol_prep
from core.features import engineering as eng


class ViolenciaAutoprovocada(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="violencia_autoprovocada",
            name="Risco de Violência Autoprovocada / Suicídio",
            description=(
                "A partir da notificação de violência, prediz o risco de o episódio ser "
                "autoprovocado (tentativa de suicídio) ou resultar em consequência suicida "
                "(CONS_SUIC=1 ou VIOL_AUTO=1). "
                "Features incluem tipo de violência, agente causador, vínculo agressor-vítima, "
                "características demográficas e orientação sexual/identidade de gênero. "
                "Utiliza SINAN-Violência."
            ),
            data_sources=["SINAN_VIOL"],
            observation_window_days=0,
            prediction_window_days=0,
            requires_linkage=False,
            icon="🚨",
            estimated_download_min=10,
            suggested_features=[
                "idade_anos", "CS_SEXO", "CS_RACA", "CS_ESCOL_N",
                "ORIENT_SEX", "IDENT_GEN", "CS_GESTANT",
                "VIOL_FISIC", "VIOL_PSICO", "VIOL_SEXU", "VIOL_NEGLI",
                "AG_ENVEN", "AG_CORTE", "AG_ENFOR",
                "REL_CONJ", "REL_EXCON", "REL_PAI", "REL_MAE",
                "AUTOR_DROGA", "VIOL_REPET",
                "age_group",
            ],
            target_col="risco_autoprovocada",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = viol_prep.preprocess(data["SINAN_VIOL"])
        # Remover consequências do target para evitar leakage parcial
        df = df.drop(columns=["CONS_DST", "CONS_GRAV", "CONS_MENT", "CONS_COMP",
                               "CONS_ESTRE", "CONS_SUIC", "VIOL_AUTO"], errors="ignore")
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()
        if "idade_anos" in df.columns:
            df["age_group"] = eng.age_group(df["idade_anos"])
            df["idade_anos"] = pd.to_numeric(df["idade_anos"], errors="coerce")
        for col in ["CS_SEXO", "CS_RACA", "CS_ESCOL_N",
                    "ORIENT_SEX", "IDENT_GEN", "CS_GESTANT", "SIT_CONJUG", "CICL_VID"]:
            if col in df.columns:
                df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)
        df = eng.clip_outliers(df, "idade_anos")
        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
