# Skill: Avaliação e Métricas — datasus-ai-prediction

Referência para interpretar, modificar ou adicionar métricas e visualizações.

**Arquivo central:** `core/models/evaluation.py`
**Calibração:** `pages/calibracao.py`
**SHAP:** integrado em `evaluation.py` e `pages/deploy.py`

---

## Funções de avaliação disponíveis

```python
from core.models.evaluation import (
    roc_chart,
    pr_chart,
    calibration_chart,
    importance_chart,
    shap_summary,
)
```

| Função               | Entrada                         | Saída (Plotly)                         |
|----------------------|---------------------------------|----------------------------------------|
| `roc_chart(y, p)`    | y_true, oof_probs               | Curva ROC com AUC no título            |
| `pr_chart(y, p)`     | y_true, oof_probs               | Curva PR + linha de baseline (prevalência) |
| `calibration_chart(y, p, n_bins=10)` | y_true, oof_probs | Scatter calibração + diagonal perfeita |
| `importance_chart(importances, top_n=20)` | feature_importances dict | Barras horizontais top-20 (usado apenas no relatório/deploy) |
| `shap_summary(model, X, max_display=20)` | pipeline treinado, X | Barras mean \|SHAP\| top-20 |
| `shap_beeswarm(model, X, max_display=15)` | pipeline treinado, X | Scatter por amostra: X=SHAP, Y=feature, cor=valor |

Todos retornam `plotly.graph_objects.Figure` — renderizar com `st.plotly_chart(fig)`.

---

## Quando usar cada métrica

| Cenário                         | Métrica preferida | Motivo                                         |
|---------------------------------|-------------------|------------------------------------------------|
| Classes balanceadas             | ROC-AUC           | Robusto e intuitivo                            |
| Classes muito desbalanceadas    | PR-AUC            | ROC-AUC pode ser otimista com muitos TN        |
| Probabilidades calibradas       | Brier Score       | Penaliza confiança excessiva                   |
| Limiar de decisão clínica       | F1 / Precision / Recall | Depende do custo de FP vs FN           |
| Comparação entre modelos        | ROC-AUC + PR-AUC  | Usar ambos para análise completa               |

---

## Interpretação da curva de calibração

```
Eixo X: Probabilidade média predita (em bins de 0.1)
Eixo Y: Fração real de positivos no bin

Diagonal perfeita = modelo bem calibrado
Curva acima da diagonal = subestimando risco (conservative)
Curva abaixo da diagonal = superestimando risco (overconfident)
```

Após treino, recalibrar com Platt scaling se a curva estiver muito desviada:
```python
from sklearn.calibration import CalibratedClassifierCV
cal = CalibratedClassifierCV(pipeline, cv="prefit", method="sigmoid")
cal.fit(X_val, y_val)
```

---

## Nomes limpos nos gráficos SHAP e Importância

Todos os gráficos que exibem nomes de features usam labels legíveis via `_label()` e `_apply_labels()` definidas no topo de `core/models/evaluation.py`:

```python
def _label(col: str) -> str:
    """Retorna o label canônico de data_dict.py, ou o nome bruto como fallback."""
    from core.features.data_dict import get_info
    base = col.rsplit("_", 1)[0] if "_" in col else col  # strip sufixo OHE
    info = get_info(col) or get_info(base)
    return info["label"] if info else col

def _apply_labels(names: list[str]) -> list[str]:
    return [_label(n) for n in names]
```

**Onde é aplicado:**

| Função                  | Como aplica                                  |
|-------------------------|----------------------------------------------|
| `importance_chart()`    | `{_label(k): v for k, v in importances}`     |
| `shap_summary()`        | `feat_labels = _apply_labels(feat_names)`    |
| `shap_beeswarm()`       | `feat_labels = _apply_labels(feat_names)`    |
| `shap_waterfall_chart()`| `index=_apply_labels(feat_names[:n])`        |
| `shap_comparison_chart()`| `top_labels = _apply_labels(top_features)`  |

**Regra:** Qualquer novo gráfico que exiba nomes de features deve chamar `_apply_labels()` antes de passar para o Plotly. Garantir que a variável esteja cadastrada em `core/features/data_dict.py`.

---

## SHAP Beeswarm

`shap_beeswarm(model, X, max_display=15)` — cada ponto é uma amostra:
- **X:** valor SHAP da feature para aquela amostra (negativo = reduz risco, positivo = aumenta)
- **Y:** posição da feature + jitter aleatório (seed=42) para separar os pontos
- **Cor:** valor normalizado da feature (azul = baixo, cinza = médio, vermelho = alto)
- Linha vertical tracejada em x=0 como referência
- Colorbar exibida apenas na última trace (evita repetição)

Na UI (`pages/analise.py`, seção `shap_global`):
```python
shap_fig = ev.shap_summary(results["model"], X_res.head(500))   # barras
shap_bee = ev.shap_beeswarm(results["model"], X_res.head(500))  # beeswarm
```
O `importance_chart` foi removido da aba SHAP Global — permanece apenas em `relatorio.py` e `deploy.py`.

---

## SHAP — lógica de extração

```python
# O pipeline tem 2 passos: preprocessor e model
preprocessor = pipeline.named_steps["preprocessor"]
model = pipeline.named_steps["model"]

X_arr = preprocessor.transform(X)  # transforma features para o modelo

# Escolha automática do explainer
if hasattr(model, "feature_importances_"):  # árvores
    explainer = shap.TreeExplainer(model)
else:                                        # modelos lineares
    explainer = shap.LinearExplainer(model, masker=shap.maskers.Independent(X_arr))

shap_values = explainer.shap_values(X_arr)

# shap_values pode ser lista (multiclasse) → extrair classe positiva
if isinstance(shap_values, list):
    shap_values = shap_values[1]
```

SHAP para deploy individual (`pages/deploy.py`): usa `waterfall_plot` em vez de `summary_plot`.

---

## Brier Score

```
Brier Score = mean((p_pred - y_true)²)

0.0 = perfeito
0.25 = modelo sem informação (prevalência = 50%)
Para prevalências diferentes de 50%:
  Brier Score ref = prevalência × (1 - prevalência)
  Brier Skill Score = 1 - (BS / BS_ref)   → quanto melhor que o naive
```

---

## Análise de Equidade por Subgrupo (`pages/analise.py` — aba Equidade)

A UI detecta automaticamente quais variáveis demográficas estão presentes na coorte e oferece estratificação por elas.

**Candidatos reconhecidos** (ordem de prioridade, em `_fairness_candidates`):

```python
# SIH / SINASC
"SEXO", "RACA_COR", "UF_SIGLA", "UF_ZI", "UF_NASC", "MUNIC_RES",

# SINAN (TB, Hanseníase, Arboviroses, AIDS, Sífilis, Violência, Intoxicação)
"CS_SEXO", "CS_RACA", "age_group",
```

A lista é filtrada para mostrar apenas colunas presentes em `cohort.columns`.

**Mapeamento por base:**

| Base     | Sexo     | Raça/Cor  | Localização | Faixa etária |
|----------|----------|-----------|-------------|--------------|
| SIH      | `SEXO`   | `RACA_COR`| `UF_SIGLA`  | `age_group`  |
| SINASC   | `SEXO`   | `RACACORMAE` | `UF_SIGLA` | `age_group_mae` |
| SINAN_*  | `CS_SEXO`| `CS_RACA` | —           | `age_group`  |

Ao adicionar suporte a uma nova base, incluir as variáveis demográficas equivalentes na lista `_fairness_candidates` em `pages/analise.py` (linha ~2367).

---

## Benchmarking por estado/período (`pages/calibracao.py`)

Objetivo: verificar se o modelo calibra bem em diferentes subgrupos.

Fluxo:
1. Treinar modelo no conjunto base
2. Para cada estado/período, filtrar os dados
3. Aplicar `calibration_chart()` separadamente
4. Visualizar curvas lado a lado para detectar drift

```python
for uf in selected_states:
    mask = X_val["UF_SIGLA"] == uf
    fig = calibration_chart(y_val[mask], probs[mask])
    st.plotly_chart(fig)
```

---

## Adicionando nova métrica

1. Calcular no `train_cv()` dentro de `core/models/pipeline.py` (junto com roc_auc, pr_auc, etc.)
2. Retornar no dict de métricas
3. Exibir na UI em `pages/analise.py` (Step 5)
4. Se precisar de gráfico: adicionar função em `core/models/evaluation.py`

---

## Métricas por fold (CV)

```python
# Retornadas por train_cv()
{
    "roc_auc":  [0.82, 0.84, 0.81, 0.83, 0.82],  # por fold
    "pr_auc":   [...],
    "f1":       [...],
    "precision":[...],
    "recall":   [...],
    "brier":    [...],
    "oof_probs": np.array([...]),   # probabilidades OOF concatenadas
    "oof_true":  np.array([...]),   # y_true OOF concatenado
}
```

Exibir como `mean ± std` com `np.mean(scores["roc_auc"])` e `np.std(...)`.
