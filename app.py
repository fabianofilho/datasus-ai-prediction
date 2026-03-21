import streamlit as st

st.set_page_config(
    page_title="DataSUS AI Prediction",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏥 DataSUS AI Prediction Platform")
st.markdown(
    """
    Plataforma de modelagem preditiva em saúde baseada nos dados abertos do **DataSUS**.

    ### Como usar

    1. **🎯 Desfecho** — Escolha o desfecho clínico que deseja prever
    2. **📥 Dados** — Baixe os dados necessários via pySUS (cache local automático)
    3. **🔬 Cohort** — Visualize e configure a janela de observação e predição
    4. **🤖 Modelo** — Selecione e treine um modelo de machine learning
    5. **📊 Resultados** — Métricas, curvas ROC, importância de variáveis (SHAP)

    ---
    ### Desfechos disponíveis

    | Desfecho | Dados | Complexidade |
    |----------|-------|-------------|
    | Readmissão hospitalar 30d | SIH | ⭐ Simples |
    | Mortalidade hospitalar | SIH + SIM | ⭐⭐ Médio |
    | Mortalidade neonatal | SINASC + SIM | ⭐⭐ Médio |
    | Abandono de tratamento TB | SINAN | ⭐⭐ Médio |

    Use o menu lateral para navegar entre as páginas.
    """
)

# Estado global da sessão
if "outcome_key" not in st.session_state:
    st.session_state["outcome_key"] = None
if "raw_data" not in st.session_state:
    st.session_state["raw_data"] = {}
if "cohort" not in st.session_state:
    st.session_state["cohort"] = None
if "model_results" not in st.session_state:
    st.session_state["model_results"] = None

# Indicador de progresso no sidebar
with st.sidebar:
    st.markdown("### Progresso")
    outcome = st.session_state.get("outcome_key")
    raw_data = st.session_state.get("raw_data", {})
    cohort = st.session_state.get("cohort")
    results = st.session_state.get("model_results")

    st.write("🎯 Desfecho:", f"**{outcome}**" if outcome else "—")
    st.write("📥 Dados:", f"**{list(raw_data.keys())}**" if raw_data else "—")
    st.write("🔬 Cohort:", f"**{len(cohort)} registros**" if cohort is not None else "—")
    st.write("🤖 Modelo:", "**Treinado**" if results else "—")
