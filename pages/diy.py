"""DataSUS AI Prediction — Do It Yourself (DIY): pipeline com base própria."""
from __future__ import annotations
from pathlib import Path
from PIL import Image as _PILImage

import streamlit as st

# ── Lazy loaders ──────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _pipeline():
    from core.models.pipeline import ALGORITHMS, train_cv
    return ALGORITHMS, train_cv

@st.cache_resource(show_spinner=False)
def _ev():
    from core.models import evaluation
    return evaluation

@st.cache_resource(show_spinner=False)
def _pd():
    import pandas as pd
    return pd

@st.cache_resource(show_spinner=False)
def _np():
    import numpy as np
    return np

# ── Page config ───────────────────────────────────────────────────────────────
_favicon = _PILImage.open(Path(__file__).parent.parent / "favicon.png")
st.set_page_config(
    page_title="DIY — DataSUS AI Prediction",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,300,0,0" />
<style>
header, footer,
[data-testid="stSidebarNav"], [data-testid="stHeader"],
[data-testid="stToolbar"], [data-testid="stDecoration"],
#MainMenu { display: none !important; }

html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {
    background: #ffffff !important;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif !important;
    color: #111827 !important;
}
.block-container { padding: 2.5rem 3rem !important; max-width: 1100px !important; }

.ms { font-family: 'Material Symbols Outlined'; font-style: normal; font-weight: normal;
      font-size: 1rem; line-height: 1; vertical-align: middle; display: inline-block; color: #111827; }
.ms-lg { font-size: 1.4rem; margin-right: .25rem; }

.diy-title { font-size: 1.4rem; font-weight: 700; color: #111827 !important;
             display: flex; align-items: center; gap: .35rem; margin-bottom: .15rem; }
.diy-sub   { font-size: .88rem; color: #6b7280 !important; margin-bottom: 1.5rem; }

.diy-step  { font-size: .68rem; font-weight: 700; color: #9ca3af !important;
             text-transform: uppercase; letter-spacing: .1em;
             margin: 1.5rem 0 .4rem; padding-bottom: .3rem;
             border-bottom: 1px solid #f3f4f6; }

.diy-info  { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px;
             padding: .6rem .9rem; font-size: .8rem; color: #374151;
             margin-bottom: .75rem; }

div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
    background-color: #111827 !important; color: #ffffff !important;
    border: 1px solid #111827 !important; border-radius: 6px !important;
    font-size: .82rem !important; font-weight: 600 !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover,
div[data-testid="stButton"] > button[data-testid="baseButton-primary"]:hover {
    background-color: #374151 !important; border-color: #374151 !important;
}
div[data-testid="stButton"] > button {
    border-radius: 6px !important; font-size: .82rem !important;
}
</style>
""", unsafe_allow_html=True)

ss = st.session_state

# ── Header ────────────────────────────────────────────────────────────────────
_back, _title_col = st.columns([1, 8])
with _back:
    if st.button("← Voltar", key="diy_back"):
        st.switch_page("app.py")

st.markdown(
    '<p class="diy-title"><span class="ms ms-lg">construction</span>Do It Yourself (DIY)</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="diy-sub">Carregue qualquer base de saúde em CSV ou Parquet, '
    'defina o desfecho e rode o pipeline preditivo completo.</p>',
    unsafe_allow_html=True,
)

# ── Step 1: Upload ─────────────────────────────────────────────────────────────
st.markdown('<p class="diy-step">1. Carregar base de dados</p>', unsafe_allow_html=True)
st.markdown(
    '<div class="diy-info">'
    '<b>Formatos aceitos:</b> CSV (separador vírgula ou ponto-e-vírgula) e Parquet. '
    'A primeira linha deve conter os nomes das colunas. '
    'O desfecho (variável alvo) deve ser binário — 0 / 1.</div>',
    unsafe_allow_html=True,
)

uploaded = st.file_uploader(
    "Selecione o arquivo",
    type=["csv", "parquet"],
    key="diy_file",
    label_visibility="collapsed",
)

if uploaded is None:
    st.stop()

pd = _pd()
np = _np()

try:
    if uploaded.name.endswith(".parquet"):
        df = pd.read_parquet(uploaded)
    else:
        try:
            df = pd.read_csv(uploaded, sep=None, engine="python", low_memory=False)
        except Exception:
            uploaded.seek(0)
            df = pd.read_csv(uploaded, sep=";", low_memory=False)
except Exception as e:
    st.error(f"Erro ao ler o arquivo: {e}")
    st.stop()

st.success(f"Base carregada: **{len(df):,} linhas × {len(df.columns)} colunas**")
with st.expander("Pré-visualização (primeiras 5 linhas)"):
    st.dataframe(df.head(5), use_container_width=True)

# ── Step 2: Definir desfecho (target) ─────────────────────────────────────────
st.markdown('<p class="diy-step">2. Variável desfecho (alvo binário)</p>', unsafe_allow_html=True)

all_cols = list(df.columns)

# Sugerir colunas binárias automaticamente
_binary_candidates = [
    c for c in all_cols
    if df[c].dropna().nunique() == 2 and set(df[c].dropna().unique()).issubset({0, 1, "0", "1", True, False})
]

target_col = st.selectbox(
    "Coluna alvo (0 = negativo, 1 = positivo)",
    options=all_cols,
    index=all_cols.index(_binary_candidates[0]) if _binary_candidates else 0,
    key="diy_target",
)

_target_vals = df[target_col].dropna().unique()
_is_binary = set(_target_vals).issubset({0, 1, "0", "1", True, False})
if not _is_binary:
    st.warning(
        f"A coluna **{target_col}** tem {len(_target_vals)} valores únicos "
        f"({sorted(_target_vals)[:5]}…). Selecione uma coluna binária (0/1)."
    )
    st.stop()

y = df[target_col].astype(int)
_pos_rate = y.mean()
_c1, _c2, _c3 = st.columns(3)
_c1.metric("Total de registros", f"{len(y):,}")
_c2.metric("Positivos (y=1)", f"{y.sum():,} ({_pos_rate:.1%})")
_c3.metric("Negativos (y=0)", f"{(~y.astype(bool)).sum():,} ({1-_pos_rate:.1%})")

# ── Step 3: Selecionar features ───────────────────────────────────────────────
st.markdown('<p class="diy-step">3. Variáveis preditoras (features)</p>', unsafe_allow_html=True)

_feature_candidates = [c for c in all_cols if c != target_col]

feature_cols = st.multiselect(
    "Selecione as colunas a usar como preditoras (deixe vazio para usar todas exceto o alvo)",
    options=_feature_candidates,
    default=[],
    key="diy_features",
)
if not feature_cols:
    feature_cols = _feature_candidates

X = df[feature_cols].copy()

st.caption(f"{len(feature_cols)} variáveis selecionadas: {', '.join(feature_cols[:8])}{'…' if len(feature_cols) > 8 else ''}")

# ── Step 4: Configurações do pipeline ─────────────────────────────────────────
st.markdown('<p class="diy-step">4. Configurações do pipeline</p>', unsafe_allow_html=True)

ALGORITHMS, train_cv = _pipeline()

_cfg1, _cfg2, _cfg3 = st.columns(3)
with _cfg1:
    algo_label = st.selectbox("Algoritmo", list(ALGORITHMS.keys()), key="diy_algo")
    algo = ALGORITHMS[algo_label]
with _cfg2:
    n_folds = st.selectbox("Folds (CV)", [3, 5, 10], index=1, key="diy_folds")
with _cfg3:
    balancing = st.selectbox(
        "Balanceamento",
        ["none", "class_weight", "smote_over", "smote_under"],
        format_func=lambda x: {
            "none": "Nenhum",
            "class_weight": "Class weight",
            "smote_over": "SMOTE (oversample)",
            "smote_under": "Undersample",
        }[x],
        key="diy_balancing",
    )

# ── Step 5: Treinar ───────────────────────────────────────────────────────────
st.markdown('<p class="diy-step">5. Treinar modelo</p>', unsafe_allow_html=True)

if st.button("Rodar pipeline", key="diy_run", type="primary"):
    with st.spinner(f"Treinando {algo_label} · {n_folds}-fold CV…"):
        try:
            results = train_cv(
                X=X, y=y,
                algorithm=algo,
                n_folds=n_folds,
                balancing=balancing,
            )
            results["X_columns"] = list(X.columns)
            ss["diy_results"] = results
            ss["diy_X"] = X.head(500)
        except Exception as _err:
            st.error(f"Erro no treinamento: {_err}")
            st.stop()

# ── Step 6: Resultados ────────────────────────────────────────────────────────
results = ss.get("diy_results")
if results is None:
    st.stop()

ev = _ev()
m  = results.get("metrics", {})

st.markdown('<p class="diy-step">6. Resultados</p>', unsafe_allow_html=True)

_m1, _m2, _m3, _m4, _m5 = st.columns(5)
_m1.metric("ROC-AUC",        f"{m.get('roc_auc', 0):.4f}")
_m2.metric("PR-AUC",         f"{m.get('pr_auc', 0):.4f}")
_m3.metric("F1",             f"{m.get('f1', 0):.4f}")
_m4.metric("Sensibilidade",  f"{m.get('recall', 0):.4f}")
_m5.metric("Especificidade", f"{m.get('specificity', 0):.4f}")

_oof    = results.get("oof_probs")
_y_eval = results.get("y_eval")

if _oof is not None and _y_eval is not None:
    import plotly.graph_objects as _go
    _y_np   = np.array(_y_eval)
    _oof_np = np.array(_oof)

    # Curvas ROC / PR
    _r1, _r2 = st.columns(2)
    with _r1:
        st.plotly_chart(ev.roc_chart(_y_np, _oof_np), use_container_width=True)
    with _r2:
        st.plotly_chart(ev.pr_chart(_y_np, _oof_np), use_container_width=True)

    # Distribuição dos scores
    st.markdown("**Distribuição dos Scores Preditos**")
    _fig_dist = _go.Figure()
    _fig_dist.add_trace(_go.Histogram(
        x=_oof_np[_y_np == 0], name="Negativo (y=0)", nbinsx=40,
        marker_color="#3b82f6", opacity=0.7,
    ))
    _fig_dist.add_trace(_go.Histogram(
        x=_oof_np[_y_np == 1], name="Positivo (y=1)", nbinsx=40,
        marker_color="#ef4444", opacity=0.7,
    ))
    _fig_dist.update_layout(
        barmode="overlay", xaxis_title="Score predito", yaxis_title="Frequência",
        height=300, margin=dict(t=20, b=40, l=40, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(_fig_dist, use_container_width=True)

    # Métricas clínicas por threshold
    st.markdown("**Métricas Clínicas por Ponto de Corte**")
    st.plotly_chart(ev.threshold_curve_chart(_y_np, _oof_np), use_container_width=True)

# SHAP
st.markdown("**Explicabilidade SHAP**")
_X_diy = ss.get("diy_X")
_model_diy = results.get("model")
if _X_diy is not None and _model_diy is not None:
    with st.spinner("Calculando SHAP…"):
        try:
            _shap_bar = ev.shap_summary(_model_diy, _X_diy)
            _shap_bee = ev.shap_beeswarm(_model_diy, _X_diy)
        except Exception:
            _shap_bar = None
            _shap_bee = None
    if _shap_bar:
        st.plotly_chart(_shap_bar, use_container_width=True)
        if _shap_bee:
            st.plotly_chart(_shap_bee, use_container_width=True)
    else:
        _fi = results.get("feature_importances", {})
        if _fi:
            st.plotly_chart(ev.importance_chart(_fi, top_n=20), use_container_width=True)
        else:
            st.info("SHAP indisponível para este algoritmo.")
