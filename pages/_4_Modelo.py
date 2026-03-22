import streamlit as st
from core.outcomes import OUTCOMES
from core.features.cohort import CohortBuilder
from core.models.pipeline import ALGORITHMS, train_cv

st.set_page_config(page_title="Modelo | DataSUS AI", page_icon="🤖", layout="wide")
st.title("🤖 Treinar Modelo")

outcome_key = st.session_state.get("outcome_key")
cohort = st.session_state.get("cohort")

if not outcome_key:
    st.warning("Selecione um desfecho primeiro.")
    st.stop()
if cohort is None:
    st.warning("Construa o cohort primeiro na página 🔬 Cohort.")
    st.stop()

outcome = OUTCOMES[outcome_key]
st.markdown(f"**Desfecho:** {outcome.icon} {outcome.name}")
st.divider()

# ── Configuração ──────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Algoritmo")
    algorithm_label = st.selectbox(
        "Selecione o algoritmo",
        options=list(ALGORITHMS.keys()),
        index=0,
        help="LightGBM é o padrão — rápido e robusto para dados clínicos.",
    )
    algorithm = ALGORITHMS[algorithm_label]

    n_folds = st.slider("Número de folds (CV)", min_value=3, max_value=10, value=5)
    use_smote = st.checkbox(
        "Usar SMOTE (oversample da classe minoritária)",
        value=False,
        help="Útil quando a prevalência do desfecho é muito baixa (<5%).",
    )

with col2:
    st.subheader("Hiperparâmetros")
    params = {}
    if algorithm in ("lgbm", "xgb", "rf"):
        params["n_estimators"] = st.slider("n_estimators (árvores)", 50, 1000, 300, 50)
    if algorithm in ("lgbm", "xgb"):
        params["learning_rate"] = st.select_slider(
            "learning_rate",
            options=[0.005, 0.01, 0.02, 0.05, 0.1, 0.2],
            value=0.05,
        )
    if algorithm in ("lgbm", "xgb", "rf"):
        params["max_depth"] = st.slider("max_depth (-1 = sem limite)", -1, 15, -1)
    if algorithm == "logreg":
        params["C"] = st.select_slider("C (regularização)", options=[0.001, 0.01, 0.1, 1.0, 10.0], value=1.0)

# ── Features ──────────────────────────────────────────────────────────────────
st.subheader("Features")
builder = CohortBuilder(outcome)
X, y = builder.get_Xy(cohort)

available_features = X.columns.tolist()
selected_features = st.multiselect(
    "Selecione as features para o modelo",
    options=available_features,
    default=available_features,
    help="Por padrão todas as features sugeridas são usadas.",
)

if not selected_features:
    st.warning("Selecione pelo menos uma feature.")
    st.stop()

X = X[selected_features]

# ── Treinar ───────────────────────────────────────────────────────────────────
st.divider()
balance_info = builder.class_balance(cohort)
st.info(
    f"Cohort: **{balance_info['total']:,}** registros | "
    f"Prevalência: **{balance_info['prevalence']:.1%}** | "
    f"Features: **{len(selected_features)}**"
)

if st.button(f"🚀 Treinar {algorithm_label} ({n_folds}-fold CV)", type="primary", use_container_width=True):
    with st.spinner(f"Treinando {algorithm_label} com {n_folds}-fold CV..."):
        try:
            results = train_cv(
                X=X, y=y,
                algorithm=algorithm,
                params=params,
                n_folds=n_folds,
                use_smote=use_smote,
            )
            st.session_state["model_results"] = results
            m = results["mean_metrics"]
            st.success(
                f"✅ Treino concluído! "
                f"ROC-AUC: **{m['roc_auc']:.4f}** | "
                f"PR-AUC: **{m['pr_auc']:.4f}** | "
                f"F1: **{m['f1']:.4f}**"
            )
        except Exception as e:
            st.error(f"Erro no treino: {e}")
            st.exception(e)

if st.session_state.get("model_results"):
    st.success("Modelo treinado! Vá para 📊 Resultados para ver as métricas detalhadas.")
