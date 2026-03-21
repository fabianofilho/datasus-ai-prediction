"""Readmissão hospitalar em 30 dias — SIH only."""

from __future__ import annotations

import pandas as pd

from core.outcomes.base import OutcomeConfig
from core.data import sih as sih_prep
from core.features import engineering as eng


class ReadmissaoHospitalar30d(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="readmissao_30d",
            name="Readmissão Hospitalar 30 dias",
            description=(
                "Prediz se um paciente será reinternado em até 30 dias após a alta hospitalar. "
                "Utiliza apenas dados do SIH-RD (internações SUS). "
                "O índice é a alta hospitalar (não morte), e o desfecho é uma nova internação "
                "dentro de 30 dias para o mesmo CNS."
            ),
            data_sources=["SIH"],
            observation_window_days=365,
            prediction_window_days=30,
            requires_linkage=False,
            icon="🔁",
            estimated_download_min=10,
            suggested_features=[
                "IDADE", "SEXO", "diag_chapter", "diag_block",
                "length_of_stay_days", "used_icu", "DIARIAS",
                "n_diag_sec", "VAL_TOT", "proc_rea_code",
                "age_group", "RACA_COR",
            ],
            target_col="readmissao_30d",
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = sih_prep.preprocess(data["SIH"])
        # Keep only alive discharges (index events)
        df = sih_prep.filter_alive_discharges(df)
        df = df.dropna(subset=["DT_SAIDA"])
        df = df.sort_values("DT_SAIDA")

        # For each discharge, check if same CNS has a new admission within 30d
        id_col = next((c for c in ["CNS_PAC", "CPF_PAC"] if c in df.columns and df[c].str.len().gt(5).any()), None)

        if id_col:
            df = _flag_readmission(df, id_col, window_days=30)
        else:
            # Fallback: no linkage possible → mark all as 0 (model still useful for exploration)
            df["readmissao_30d"] = 0

        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()

        # ICD-10 encoding
        if "DIAG_PRINC" in df.columns:
            df["diag_chapter"] = eng.icd10_chapter(df["DIAG_PRINC"])
            df["diag_block"] = eng.icd10_block(df["DIAG_PRINC"])

        # Number of secondary diagnoses
        if "DIAG_SEC" in df.columns:
            df["n_diag_sec"] = (~df["DIAG_SEC"].isna()).astype(int)

        # Age group
        if "IDADE" in df.columns:
            df["age_group"] = eng.age_group(df["IDADE"])

        # Procedure code
        if "PROC_REA" in df.columns:
            df["proc_rea_code"] = pd.Categorical(df["PROC_REA"].astype(str)).codes.astype(float)

        # Sex binary
        if "SEXO" in df.columns:
            df["SEXO"] = pd.Categorical(df["SEXO"].astype(str)).codes.astype(float)

        # Race
        if "RACA_COR" in df.columns:
            df["RACA_COR"] = pd.Categorical(df["RACA_COR"].astype(str)).codes.astype(float)

        # Clip outliers on length of stay
        df = eng.clip_outliers(df, "length_of_stay_days")
        df = eng.clip_outliers(df, "VAL_TOT")

        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)


def _flag_readmission(df: pd.DataFrame, id_col: str, window_days: int) -> pd.DataFrame:
    """For each row, check if the same patient was admitted within window_days after DT_SAIDA."""
    df = df.copy()
    df["readmissao_30d"] = 0

    # Group by patient ID
    patient_admissions = df[df[id_col].str.len() > 5].groupby(id_col)["DT_INTER"].apply(list).to_dict()

    for idx, row in df.iterrows():
        pid = row.get(id_col, "")
        discharge = row.get("DT_SAIDA")
        if not pid or pd.isna(discharge):
            continue
        admissions = patient_admissions.get(pid, [])
        for adm in admissions:
            if pd.notna(adm) and 0 < (adm - discharge).days <= window_days:
                df.at[idx, "readmissao_30d"] = 1
                break

    return df
