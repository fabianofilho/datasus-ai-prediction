"""Infecção hospitalar adquirida durante internação — SIH."""

from __future__ import annotations

import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sih as sih_prep
from core.features import engineering as eng


class InfeccaoHospitalar(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="infeccao_hospitalar",
            name="Infecção Hospitalar",
            description=(
                "Prediz o risco de infecção hospitalar adquirida durante a internação "
                "(campo INFEHOSP do SIH-RD). Features incluem diagnóstico de admissão, "
                "tempo de permanência, uso de UTI e características do paciente."
            ),
            data_sources=["SIH"],
            observation_window_days=0,
            prediction_window_days=30,
            requires_linkage=False,
            icon="🦠",
            estimated_download_min=10,
            suggested_features=[
                "IDADE", "SEXO", "diag_chapter", "used_icu",
                "length_of_stay_days", "CAR_INT", "RACA_COR",
                "age_group", "PROC_REA",
            ],
            target_col="infeccao_hospitalar",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = sih_prep.preprocess(data["SIH"])

        if "INFEHOSP" in data["SIH"].columns:
            raw = data["SIH"]["INFEHOSP"].astype(str).str.strip()
            positivos = raw.isin(["1", "S", "SIM"]).sum()
            if positivos == 0:
                # INFEHOSP é sub-notificado no SIH-RD público: campo raramente preenchido.
                # Usar como proxy: diagnóstico secundário com CID-10 capítulo I (infecções).
                diag_sec = data["SIH"].get("DIAGSEC1", data["SIH"].get("DIAG_SECUN", pd.Series(dtype=str)))
                # T80–T88 = complicações de procedimentos; A/B = doenças infecciosas
                sec = diag_sec.astype(str).str.upper()
                df["infeccao_hospitalar"] = (
                    sec.str.startswith("T8") | sec.str.startswith("A") | sec.str.startswith("B")
                ).astype(int)
            else:
                df["infeccao_hospitalar"] = raw.isin(["1", "S", "SIM"]).astype(int)
        else:
            df["infeccao_hospitalar"] = 0

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
        df = eng.clip_outliers(df, "VAL_TOT")

        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
