"""Pima Indians Diabetes — UCI 1990. CSV público, sem credencial."""
from __future__ import annotations

import pandas as pd

URL = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"

_COLUMNS = [
    "pregnancies",
    "glucose",
    "blood_pressure",
    "skin_thickness",
    "insulin",
    "bmi",
    "diabetes_pedigree",
    "age",
    "target",
]

DICT_META = {
    "pregnancies":       {"label": "Gestações prévias",         "desc": "Número de gestações", "type": "Numérica"},
    "glucose":           {"label": "Glicose plasmática 2h",     "desc": "Concentração de glicose após TOTG (mg/dL)", "type": "Numérica"},
    "blood_pressure":    {"label": "Pressão diastólica",        "desc": "mmHg", "type": "Numérica"},
    "skin_thickness":    {"label": "Espessura prega tricipital","desc": "mm", "type": "Numérica"},
    "insulin":           {"label": "Insulina sérica 2h",        "desc": "mu U/mL", "type": "Numérica"},
    "bmi":               {"label": "IMC",                       "desc": "kg/m²", "type": "Numérica"},
    "diabetes_pedigree": {"label": "Pedigree diabetes",         "desc": "Função de hereditariedade familiar", "type": "Numérica"},
    "age":               {"label": "Idade",                     "desc": "Anos", "type": "Numérica"},
    "target":            {"label": "Diabetes",                  "desc": "Desfecho binário em 5 anos (0/1)", "type": "Derivada"},
}


def load() -> pd.DataFrame:
    """Baixa e devolve o Pima como DataFrame com colunas nomeadas e target 0/1.

    Valores 0 em glucose/blood_pressure/skin_thickness/insulin/bmi são
    fisiologicamente impossíveis e representam missing — substituídos por NaN.
    """
    df = pd.read_csv(URL, header=None, names=_COLUMNS)
    for col in ("glucose", "blood_pressure", "skin_thickness", "insulin", "bmi"):
        df[col] = df[col].replace(0, pd.NA)
    df["target"] = df["target"].astype(int)
    return df
