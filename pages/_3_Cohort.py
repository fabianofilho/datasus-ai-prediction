import streamlit as st
import pandas as pd
import plotly.express as px
from core.outcomes import OUTCOMES
from core.features.cohort import CohortBuilder

st.set_page_config(page_title="Cohort | DataSUS AI", page_icon="🔬", layout="wide")
st.title("🔬 Construir Cohort")

outcome_key = st.session_state.get("outcome_key")
raw_data = st.session_state.get("raw_data", {})

if not outcome_key:
    st.warning("Selecione um desfecho primeiro.")
    st.stop()
if not raw_data:
    st.warning("Baixe os dados primeiro na página 📥 Dados.")
    st.stop()

outcome = OUTCOMES[outcome_key]
st.markdown(f"**Desfecho:** {outcome.icon} {outcome.name}")
st.divider()

if st.button("🔨 Construir Cohort", type="primary", use_container_width=True):
    with st.spinner("Construindo cohort... (pode levar alguns minutos)"):
        try:
            builder = CohortBuilder(outcome)
            cohort = builder.build(raw_data)
            st.session_state["cohort"] = cohort
            st.session_state["model_results"] = None
            st.success(f"Cohort construído: **{len(cohort):,}** registros.")
        except Exception as e:
            st.error(f"Erro ao construir cohort: {e}")
            st.exception(e)

cohort = st.session_state.get("cohort")
if cohort is None:
    st.info("Clique em 'Construir Cohort' para processar os dados.")
    st.stop()

# ── Balanceamento de classes ──────────────────────────────────────────────────
builder = CohortBuilder(outcome)
balance = builder.class_balance(cohort)

st.subheader("Balanceamento de Classes")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total", f"{balance['total']:,}")
c2.metric("Positivos (desfecho=1)", f"{balance['positive']:,}")
c3.metric("Negativos (desfecho=0)", f"{balance['negative']:,}")
c4.metric("Prevalência", f"{balance['prevalence']:.1%}")

fig = px.pie(
    values=[balance["positive"], balance["negative"]],
    names=["Positivo (1)", "Negativo (0)"],
    color_discrete_sequence=["#d62728", "#1f77b4"],
    title="Distribuição do Desfecho",
)
st.plotly_chart(fig, use_container_width=False)

# ── Feature preview ───────────────────────────────────────────────────────────
st.subheader("Preview do Cohort")
st.dataframe(cohort.head(100), use_container_width=True)

# ── Missing values ────────────────────────────────────────────────────────────
st.subheader("Dados Faltantes (% por coluna)")
missing = (cohort.isnull().mean() * 100).sort_values(ascending=False)
missing = missing[missing > 0].head(20)
if not missing.empty:
    fig_miss = px.bar(
        x=missing.values,
        y=missing.index,
        orientation="h",
        labels={"x": "% faltante", "y": "coluna"},
        title="Top colunas com dados faltantes",
        color=missing.values,
        color_continuous_scale="Reds",
    )
    st.plotly_chart(fig_miss, use_container_width=True)
else:
    st.success("Nenhum dado faltante nas colunas selecionadas!")

st.success("Cohort pronto. Vá para 🤖 Modelo para treinar o modelo.")
