# Skill: Pipeline ML — datasus-ai-prediction

Referência para modificar, entender ou depurar o pipeline de treinamento.

**Arquivo central:** `core/models/pipeline.py`
**Avaliação:** `core/models/evaluation.py`

---

## Estrutura do pipeline (sklearn Pipeline)

```
SentinelReplacer(sentinel_values=[9, 99])
    → ColumnTransformer (encoding + scaling por coluna)
        → [opcional] StandardScaler (apenas para LogReg)
        → [opcional] SMOTE / SMOTETomek (balanceamento)
            → Model
```

Função de entrada: `build_pipeline(X, algorithm, params, balancing, treatment)`

---

## Algoritmos disponíveis

| Chave          | Classe                        | Notas                                     |
|----------------|-------------------------------|-------------------------------------------|
| `lgbm`         | `LGBMClassifier`              | Padrão: 300 trees, LR=0.05, leaves=31    |
| `xgboost`      | `XGBClassifier`               | tree_method='hist', n_jobs=-1             |
| `catboost`     | `CatBoostClassifier`          | auto_class_weights='Balanced', verbose=0  |
| `logreg`       | `LogisticRegression`          | max_iter=1000; aplica StandardScaler      |
| `rf`           | `RandomForestClassifier`      | n_jobs=-1                                 |
| `tabpfn`       | `TabPFNClassifier`            | Máx 10K amostras; 8 estimadores           |

---

## Balanceamento de classes

| Modo           | Mecanismo                          |
|----------------|------------------------------------|
| `class_weight` | `class_weight='balanced'` no modelo (padrão) |
| `smote_over`   | SMOTE (oversampling da classe minoritária)    |
| `smote_under`  | SMOTETomek (over + undersampling combinados)  |
| `none`         | Sem balanceamento                             |

---

## Encoding de features

Configurado no `ColumnTransformer` dentro de `_build_preprocessor()`:

| Tipo     | Estratégia                                          |
|----------|-----------------------------------------------------|
| Numérica | `SimpleImputer(median)` + scaling opcional          |
| Categórica | `SimpleImputer(most_frequent)` + encoding         |

Opções de encoding:
- `ohe` — OneHotEncoder (para modelos lineares)
- `ordinal` — OrdinalEncoder (padrão para árvores)
- `target` — TargetEncoder (alta cardinalidade)
- `none` — sem encoding adicional (ordinal passthrough)

Opções de scaling:
- `none` — sem scaling (padrão para árvores)
- `standard` — StandardScaler
- `minmax` — MinMaxScaler
- `robust` — RobustScaler
- `bin` — KBinsDiscretizer (transforma numérica em bins)

---

## Tratamento de sentinel values (SentinelReplacer)

DATASUS usa 9 e 99 para "desconhecido/ignorado". O `SentinelReplacer` substitui esses valores por `NaN` **antes** do imputer, evitando que sejam tratados como dados válidos.

```python
# Aplicado automaticamente no pipeline
SentinelReplacer(sentinel_values=[9, 99])
```

---

## Cross-validation

```python
train_cv(X, y, pipeline, cv=StratifiedKFold(5, shuffle=True, random_state=42))
```

- Retorna OOF (out-of-fold) predictions concatenadas
- Métricas por fold: ROC-AUC, PR-AUC, F1, Precision, Recall, Brier Score
- Resultado: `mean ± std` de cada métrica

---

## Busca de hiperparâmetros

| Modo            | Função                        | Grids          |
|-----------------|-------------------------------|----------------|
| `random`        | `RandomizedSearchCV`          | `_RANDOM_GRIDS` |
| `grid`          | `GridSearchCV`                | `_GRID_GRIDS`  |
| `optuna`        | Bayesian TPE (Optuna)         | Espaço contínuo|

Exemplos de grids (LightGBM):
- Random: n_estimators ∈ {100,200,300,500,800}, LR ∈ {0.005,0.01,0.05,0.1,0.2}, depth ∈ {-1,3,5,7,10}
- Optuna: trial.suggest_int / suggest_float com pruning (MedianPruner)

---

## Calibração pós-treino

```python
from sklearn.calibration import CalibratedClassifierCV

calibrated = CalibratedClassifierCV(
    estimator=pipeline,
    cv="prefit",          # modelo já treinado
    method="sigmoid"      # Platt scaling
)
calibrated.fit(X_val, y_val)
```

Alternativa: `method="isotonic"` (não paramétrico, precisa de mais dados).

---

## Adicionando novo algoritmo

1. Adicionar a lógica em `_build_model(algorithm, params)` em `core/models/pipeline.py`
2. Adicionar grid em `_RANDOM_GRIDS` e `_GRID_GRIDS`
3. Adicionar espaço Optuna no bloco `if algorithm == "novo"` da função `optimize_hyperparams()`
4. Adicionar a chave em `ALGORITHMS` (dict com nome de exibição)

---

## Fluxo completo na UI (`pages/analise.py`)

```
Step 1: selecionar desfecho (outcome_key)
Step 2: download + pré-processamento (core/data/*.py)
Step 3: build_cohort() + build_features() → X, y
Step 4: build_pipeline() → train_cv() → [optimize_hyperparams()]
Step 5: roc_chart() + pr_chart() + calibration_chart() + shap_summary()
```
