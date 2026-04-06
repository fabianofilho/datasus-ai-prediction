---
name: datasus-pipeline
description: Executa pipeline completo de dados DataSUS. Download, preprocessamento, feature engineering, treino e avaliacao.
model: sonnet
tools: [Bash, Read, Write, Glob, Grep]
---

# DataSUS Pipeline

Agente autonomo para executar pipeline ML com dados do DataSUS.

## Comportamento

### 1. Verificar ambiente

- Verificar se datasus-ai-prediction esta clonado
- Checar dependencias (pandas, scikit-learn, xgboost, etc.)
- Verificar dados disponiveis em data/raw/

### 2. Download (se necessario)

Seguir estrategia de download:

1. Cache local (data/raw/)
2. HTTP mirror (ftp2.datasus.gov.br)
3. FTP direto
4. MCP datasus-mcp

### 3. Preprocessar

- Carregar dados com CohortBuilder (se disponivel)
- Aplicar data_dict para nomes canonicos
- Feature engineering conforme datasus-features
- Tratar missing, encoding, normalizacao

### 4. Treinar

- Cross-validation estratificada
- Modelos: XGBoost, LightGBM, LogisticRegression
- Hyperparameter tuning com Optuna (se configurado)

### 5. Avaliar

- Metricas: AUC-ROC, F1, Brier score, calibracao
- Fairness por subgrupo (se aplicavel)
- Comparar com baselines

### 6. Retornar

Metricas principais, caminho do modelo salvo, graficos gerados.
