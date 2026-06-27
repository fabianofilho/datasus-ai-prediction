"""Heart Disease UCI Cleveland (processed). CSV público, sem credencial."""
from __future__ import annotations

import pandas as pd

URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"

_COLUMNS = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num",
]

DICT_META = {
    "age":      {"label": "Idade",                       "desc": "Anos", "type": "Numérica"},
    "sex":      {"label": "Sexo",                        "desc": "1=masculino, 0=feminino", "type": "Categórica"},
    "cp":       {"label": "Tipo de dor torácica",        "desc": "1=típica, 2=atípica, 3=não-anginosa, 4=assintomática", "type": "Categórica"},
    "trestbps": {"label": "PA sistólica em repouso",     "desc": "mmHg na admissão", "type": "Numérica"},
    "chol":     {"label": "Colesterol total",            "desc": "mg/dL", "type": "Numérica"},
    "fbs":      {"label": "Glicemia jejum > 120 mg/dL",  "desc": "1=sim, 0=não", "type": "Categórica"},
    "restecg":  {"label": "ECG em repouso",              "desc": "0=normal, 1=anormalidade ST-T, 2=HVE", "type": "Categórica"},
    "thalach":  {"label": "FC máxima atingida",          "desc": "bpm em teste de esforço", "type": "Numérica"},
    "exang":    {"label": "Angina induzida por esforço", "desc": "1=sim, 0=não", "type": "Categórica"},
    "oldpeak":  {"label": "Depressão ST",                "desc": "Pós-exercício vs repouso", "type": "Numérica"},
    "slope":    {"label": "Inclinação ST pico",          "desc": "1=ascendente, 2=plano, 3=descendente", "type": "Categórica"},
    "ca":       {"label": "Vasos com fluorose",          "desc": "Número 0-3", "type": "Ordinal"},
    "thal":     {"label": "Cintilografia talêmica",      "desc": "3=normal, 6=defeito fixo, 7=reversível", "type": "Categórica"},
    "target":   {"label": "Doença coronariana",          "desc": "1=presença (estenose >50%), 0=ausência", "type": "Derivada"},
}


def load() -> pd.DataFrame:
    """Baixa Cleveland processed e devolve com target binário (0 / 1).

    Original: `num` 0–4 (severidade). Colapsado em binário (>=1 → 1).
    Missing marcados como '?' no arquivo, convertidos para NaN.
    """
    df = pd.read_csv(URL, header=None, names=_COLUMNS, na_values="?")
    df["target"] = (df["num"].fillna(0).astype(float) >= 1).astype(int)
    df = df.drop(columns=["num"])
    return df
