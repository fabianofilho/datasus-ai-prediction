"""Mortalidade hospitalar — SIH + SIM."""

from __future__ import annotations

import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sih as sih_prep, sim as sim_prep
from core.data.linker import link_sih_sim
from core.features import engineering as eng


class MortalidadeHospitalar(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="mortalidade_hospitalar",
            name="Mortalidade Hospitalar",
            description=(
                "Prediz o risco de óbito durante a internação ou em até 30 dias após a alta. "
                "Combina o campo MOT_SAIDA do SIH (óbito na alta) com record linkage ao SIM "
                "(para capturar mortes pós-alta). "
                "Requer dados do SIH e do SIM para o mesmo estado e ano."
            ),
            data_sources=["SIH", "SIM"],
            observation_window_days=0,
            prediction_window_days=30,
            requires_linkage=True,
            icon="💀",
            estimated_download_min=15,
            suggested_features=[
                "IDADE", "SEXO", "diag_chapter", "diag_block",
                "length_of_stay_days", "used_icu", "DIARIAS",
                "n_diag_sec", "VAL_TOT", "CAR_INT_code",
                "age_group", "RACA_COR", "proc_rea_code",
            ],
            target_col="obito",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        sih = sih_prep.preprocess(data["SIH"])

        if "SIM" in data and data["SIM"] is not None:
            sim = sim_prep.preprocess(data["SIM"])
            df = link_sih_sim(sih, sim, window_days=self.prediction_window_days)
            # Death = in-hospital death OR linked death post-discharge
            df["obito"] = ((df.get("is_death", 0) == 1) | (df.get("linked_death", 0) == 1)).astype(int)
        else:
            # SIM not available — use MOT_SAIDA only
            sih["obito"] = sih.get("is_death", pd.Series(0, index=sih.index))
            df = sih

        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()

        if "DIAG_PRINC" in df.columns:
            df["diag_chapter"] = eng.icd10_chapter(df["DIAG_PRINC"])
            df["diag_block"] = eng.icd10_block(df["DIAG_PRINC"])

        if "DIAG_SEC" in df.columns:
            df["n_diag_sec"] = (~df["DIAG_SEC"].isna()).astype(int)

        if "IDADE" in df.columns:
            df["age_group"] = eng.age_group(df["IDADE"])

        if "SEXO" in df.columns:
            df["SEXO"] = pd.Categorical(df["SEXO"].astype(str)).codes.astype(float)

        if "RACA_COR" in df.columns:
            df["RACA_COR"] = pd.Categorical(df["RACA_COR"].astype(str)).codes.astype(float)

        if "CAR_INT" in df.columns:
            df["CAR_INT_code"] = pd.Categorical(df["CAR_INT"].astype(str)).codes.astype(float)

        if "PROC_REA" in df.columns:
            df["proc_rea_code"] = pd.Categorical(df["PROC_REA"].astype(str)).codes.astype(float)

        df = eng.clip_outliers(df, "length_of_stay_days")
        df = eng.clip_outliers(df, "VAL_TOT")

        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
