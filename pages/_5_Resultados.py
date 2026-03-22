import streamlit as st
import pandas as pd
import numpy as np
from core.outcomes import OUTCOMES
from core.features.cohort import CohortBuilder
from core.models import evaluation as ev

st.set_page_config(page_title="Resultados | DataSUS AI", page_icon="📊", layout="wide")
st.title("📊 Resultados")

outcome_key = st.session_state.get("outcome_key")
cohort = st.session_state.get("cohort")
results = st.session_state.get("model_results")

if not outcome_key:
    st.warning("Selecione um desfecho primeiro.")
    st.stop()
if cohort is None:
    st.warning("Construa o cohort primeiro.")
    st.stop()
if results is None:
    st.warning("Treine o modelo primeiro na página 🤖 Modelo.")
    st.stop()

outcome = OUTCOMES[outcome_key]
st.markdown(f"**Desfecho:** {outcome.icon} {outcome.name} | **Algoritmo:** {results['algorithm']}")
st.divider()

# ── Métricas agregadas ────────────────────────────────────────────────────────
st.subheader("Métricas (média 5-fold OOF)")
m = results["mean_metrics"]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("ROC-AUC", f"{m['roc_auc']:.4f}")
c2.metric("PR-AUC", f"{m['pr_auc']:.4f}")
c3.metric("F1", f"{m['f1']:.4f}")
c4.metric("Recall", f"{m['recall']:.4f}")
c5.metric("Brier Score", f"{m['brier']:.4f}")

# ── Por fold ─────────────────────────────────────────────────────────────────
with st.expander("📋 Métricas por fold"):
    st.dataframe(ev.fold_metrics_table(results["fold_metrics"]), use_container_width=True)

st.divider()

# ── Curvas ────────────────────────────────────────────────────────────────────
builder = CohortBuilder(outcome)
X, y = builder.get_Xy(cohort)
X = X[results["X_columns"]]
y_arr = y.values
oof = results["oof_probs"]

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(ev.roc_chart(y_arr, oof), use_container_width=True)
with col2:
    st.plotly_chart(ev.pr_chart(y_arr, oof), use_container_width=True)

st.plotly_chart(ev.calibration_chart(y_arr, oof), use_container_width=False)

st.divider()

# ── Importância de variáveis ──────────────────────────────────────────────────
st.subheader("Importância das Variáveis")

if results.get("feature_importances"):
    st.plotly_chart(ev.importance_chart(results["feature_importances"]), use_container_width=False)

# SHAP
st.subheader("SHAP — Explicabilidade")
with st.spinner("Calculando valores SHAP (pode levar alguns minutos)..."):
    shap_fig = ev.shap_summary(results["model"], X.head(500))
if shap_fig:
    st.plotly_chart(shap_fig, use_container_width=False)
else:
    st.info("SHAP não disponível para este algoritmo/versão. Instale: `pip install shap`")

st.divider()

# ── Distribuição de scores ────────────────────────────────────────────────────
st.subheader("Distribuição dos Scores Preditos")
import plotly.express as px
fig_dist = px.histogram(
    x=oof,
    color=y_arr.astype(str),
    nbins=50,
    barmode="overlay",
    opacity=0.65,
    labels={"x": "Score predito", "color": "Desfecho real"},
    color_discrete_map={"0": "#1f77b4", "1": "#d62728"},
    title="Distribuição dos Scores por Classe Real",
)
st.plotly_chart(fig_dist, use_container_width=True)

st.divider()

# ── Export ────────────────────────────────────────────────────────────────────
st.subheader("Exportar Predições")
export_df = pd.DataFrame({"score": oof, "predicao": (oof >= 0.5).astype(int), "real": y_arr})
csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Baixar predições OOF (CSV)",
    data=csv,
    file_name=f"predicoes_{outcome_key}.csv",
    mime="text/csv",
)
