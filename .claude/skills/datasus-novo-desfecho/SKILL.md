# Skill: Criar Novo Desfecho (Outcome) — datasus-ai-prediction

Use este guia sempre que precisar criar, modificar ou registrar um novo desfecho preditivo no projeto.

---

## Arquitetura

```
core/outcomes/
├── base.py           ← classe abstrata OutcomeConfig
├── __init__.py       ← _REGISTRY, OUTCOMES (lazy), OUTCOME_GROUPS
├── prematuridade.py  ← exemplo de referência
└── {novo_desfecho}.py
```

A UI em `app.py` lê `OUTCOME_GROUPS` de `core/outcomes/__init__.py` (não de `app.py`).

---

## Passo 1 — Criar `core/outcomes/{chave}.py`

```python
"""Descrição curta — BASE (ex: SINASC)."""
from __future__ import annotations
import pandas as pd
from core.outcomes.base import OutcomeConfig
from core.data import {preprocessador} as prep   # ex: sinasc, sih, sinan
from core.features import engineering as eng

class NomeClasse(OutcomeConfig):
    def __init__(self):
        super().__init__(
            key="chave_snake_case",          # único, usado em session_state
            name="Nome para exibição",
            description="Parágrafo descrevendo o desfecho e as features.",
            data_sources=["SINASC"],         # lista: "SIH", "SIM", "SINAN_TB", etc.
            observation_window_days=0,       # 0 = sem janela histórica (estático)
            prediction_window_days=0,        # 0 = desfecho definido no evento índice
            requires_linkage=False,          # True apenas se cruzar 2 sistemas
            icon="nome_material_symbol",     # ícone do Material Symbols (string)
            estimated_download_min=5,        # estimativa para a UI
            suggested_features=[             # colunas que entram no X
                "COLUNA_A", "COLUNA_B", "feature_derivada",
            ],
            target_col="nome_do_target",     # nome da coluna alvo no cohort
        )

    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        df = prep.preprocess(data["FONTE"])
        # Definir target — ex: df["nome_do_target"] = (df["COL"] == valor).astype(int)
        # REMOVER colunas que causariam leakage (ex: a própria coluna que define o target)
        df = df.drop(columns=["COL_LEAKAGE"], errors="ignore")
        return df

    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        df = cohort.copy()
        # Encoding de categóricas
        for col in ["COL_CAT_1", "COL_CAT_2"]:
            if col in df.columns:
                df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)
        # Numéricas
        if "IDADE" in df.columns:
            df["IDADE"] = pd.to_numeric(df["IDADE"], errors="coerce")
            df["age_group"] = eng.age_group(df["IDADE"])
        # Remover colunas que vazam o target
        df = df.drop(columns=["COL_LEAKAGE_2"], errors="ignore")
        return df

    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        return cohort[self.target_col].fillna(0).astype(int)
```

---

## Passo 2 — Registrar em `core/outcomes/__init__.py`

Adicionar entrada no dicionário `_REGISTRY`:

```python
"chave_snake_case": {
    "module": "core.outcomes.chave_snake_case",
    "class":  "NomeClasse",
    "name":   "Nome para exibição",
    "description": "Mesmo texto do __init__ da classe.",
    "data_sources": ["SINASC"],
    "icon": "nome_material_symbol",
    "estimated_download_min": 5,
},
```

E adicionar a chave no grupo correto em `OUTCOME_GROUPS`:

```python
OUTCOME_GROUPS: dict[str, list[str]] = {
    "Saúde Materno-Infantil": ["baixo_peso_nascer", ..., "chave_snake_case"],
    ...
}
```

---

## Passo 3 — Adicionar em `app.py`

O `app.py` tem seu próprio `OUTCOME_GROUPS` dict (separado do de `__init__.py`) para a tela inicial. Adicionar o card ao grupo correspondente:

```python
{
    "key":     "chave_snake_case",
    "icon":    "nome_material_symbol",
    "name":    "Nome para exibição",
    "source":  "SINASC",          # fonte de dados principal
    "est_min": 5,
    "status":  "ok",              # "ok" = pipeline completo, "dev" = em desenvolvimento
    "linkage": None,              # ou string descrevendo o linkage se requires_linkage=True
    "note":    "Nota curta sobre a base e disponibilidade.",
},
```

---

## Regras anti-leakage

- **SINASC:** não incluir `GESTACAO` em prematuridade; não incluir `PESO` em baixo_peso_nascer; não incluir `APGAR5` em apgar_baixo.
- **SIH:** não incluir `MORTE` ou `DIAS_PERM` como feature quando o target deriva delas.
- **SINAN:** não incluir `SITUA_ENCE` como feature quando o target é derivado dela.
- Remover com `df.drop(columns=[...], errors="ignore")` no `build_cohort()`.

---

## Fontes de dados disponíveis

| data_sources key | Preprocessador            | Arquivo DBC         |
|------------------|---------------------------|---------------------|
| SINASC           | `core.data.sinasc`        | DN{UF}{ano}.dbc     |
| SIH              | `core.data.sih`           | RD{UF}{ano}{mes}.dbc|
| SIM              | `core.data.sim`           | DO{UF}{ano}.dbc     |
| SINAN_TB         | `core.data.sinan`         | TUBEBR{ano}.dbc     |
| SINAN_HANS       | `core.data.sinan_hans`    | HANSBR{ano}.dbc     |
| SINAN_DENG       | `core.data.sinan_deng` (ou similar) | DENGBR{ano}.dbc |
| SINAN_AIDS       | `core.data.sinan_aids`    | AIDABR{ano}.dbc     |
| SINAN_SIFA       | `core.data.sinan_sifa`    | SIFABR{ano}.dbc     |
| SINAN_VIOL       | `core.data.sinan_viol`    | VIOLBR{ano}.dbc     |
| SINAN_IEXO       | `core.data.sinan_iexo`    | IEXOBR{ano}.dbc     |
| SINAN_CHIK       | `core.data.sinan_chik`    | CHIKBR{ano}.dbc     |

---

## Referência: `core/outcomes/prematuridade.py`
Exemplo completo e funcional de desfecho de base única (SINASC), sem linkage, com feature engineering simples.
