"""Tempo de permanência prolongada — SIH."""

from __future__ import annotations

import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sih as sih_prep
from core.features import engineering as eng

THRESHOLD_DAYS = 15


class PermanenciaProlongada(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="permanencia_prolongada",
            name="Permanência Hospitalar Prolongada",
            description=(
                f"Prediz a probabilidade de uma internação exceder {THRESHOLD_DAYS} dias, "
                "auxiliando no planejamento de leitos e identificação de casos complexos. "
                "Utiliza características de admissão do SIH-RD."
            ),
            data_sources=["SIH"],
            observation_window_days=0,
            prediction_window_days=THRESHOLD_DAYS,
            requires_linkage=False,
            icon="🛏️",
            estimated_download_min=10,
            suggested_features=[
                "IDADE", "SEXO", "diag_chapter", "diag_block",
                "used_icu", "CAR_INT", "RACA_COR",
                "PROC_REA", "age_group",
            ],
            target_col="permanencia_prolongada",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = sih_prep.preprocess(data["SIH"])
        df["permanencia_prolongada"] = (
            df["length_of_stay_days"].fillna(0) > THRESHOLD_DAYS
        ).astype(int)
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()

        if "DIAG_PRINC" in df.columns:
            df["diag_chapter"] = eng.icd10_chapter(df["DIAG_PRINC"])
            df["diag_block"] = eng.icd10_block(df["DIAG_PRINC"])

        if "IDADE" in df.columns:
            df["age_group"] = eng.age_group(df["IDADE"])
            df["IDADE"] = pd.to_numeric(df["IDADE"], errors="coerce")

        for col in ["SEXO", "RACA_COR", "CAR_INT"]:
            if col in df.columns:
                df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)

        if "PROC_REA" in df.columns:
            df["proc_rea_code"] = pd.Categorical(df["PROC_REA"].astype(str)).codes.astype(float)

        df = eng.clip_outliers(df, "VAL_TOT")

        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
