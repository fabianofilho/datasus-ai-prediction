"""Custo hospitalar elevado (> percentil 90) — SIH."""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sih as sih_prep
from core.features import engineering as eng

COST_PERCENTILE = 90


class CustoHospitalarElevado(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="custo_elevado",
            name="Custo Hospitalar Elevado",
            description=(
                f"Prediz a probabilidade de uma internação gerar custo acima do "
                f"percentil {COST_PERCENTILE} da distribuição de custos (VAL_TOT). "
                "Auxilia no planejamento financeiro e identificação de casos de alta complexidade."
            ),
            data_sources=["SIH"],
            observation_window_days=0,
            prediction_window_days=30,
            requires_linkage=False,
            icon="💰",
            estimated_download_min=10,
            suggested_features=[
                "IDADE", "SEXO", "diag_chapter", "diag_block",
                "used_icu", "CAR_INT", "length_of_stay_days",
                "RACA_COR", "age_group", "PROC_REA",
            ],
            target_col="custo_elevado",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = sih_prep.preprocess(data["SIH"])

        if "VAL_TOT" in df.columns:
            val = pd.to_numeric(df["VAL_TOT"], errors="coerce")
            threshold = np.nanpercentile(val.dropna(), COST_PERCENTILE)
            df["custo_elevado"] = (val > threshold).astype(int)
        else:
            df["custo_elevado"] = 0

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

        df = eng.clip_outliers(df, "length_of_stay_days")

        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
