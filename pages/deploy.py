"""DataSUS AI Prediction — Deploy: inferência individual com SHAP local."""
from __future__ import annotations
from pathlib import Path
from PIL import Image as _PILImage

import streamlit as st
from core.outcomes import OUTCOMES

@st.cache_resource(show_spinner=False)
def _cohort():
    from core.features.cohort import CohortBuilder
    return CohortBuilder

@st.cache_resource(show_spinner=False)
def _ev():
    from core.models import evaluation
    return evaluation

@st.cache_resource(show_spinner=False)
def _pd():
    import pandas as pd
    return pd

_favicon = _PILImage.open(Path(__file__).parent.parent / "favicon.png")
st.set_page_config(
    page_title="Deploy — DataSUS AI",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,300,0,0" />
<style>
:root {
  --primary:#111827; --bg:#ffffff; --fg:#111827;
  --muted:#6b7280; --border:#e5e7eb; --radius:6px; --topbar-h:52px;
}
header,footer,[data-testid="stSidebarNav"],[data-testid="stHeader"],
[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu{display:none!important}
html,body,.stApp,[data-testid="stAppViewContainer"]{
  background:var(--bg)!important;
  font-family:-apple-system,BlinkMacSystemFont,"Inter","Segoe UI",sans-serif!important;
  color:var(--fg)!important;
}
.block-container{
  padding-top:calc(var(--topbar-h)+32px)!important;
  padding-bottom:56px!important;
  padding-left:40px!important;padding-right:40px!important;
  max-width:1100px!important;
}
.ds-topbar{
  position:fixed;top:0;left:0;right:0;z-index:9999;
  height:var(--topbar-h);background:var(--bg);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
  padding:0 48px 0 calc(52px+20px);
}
.ds-topbar-logo{
  display:flex;align-items:center;gap:8px;
  font-size:0.93rem;font-weight:700;color:#111827!important;text-decoration:none!important;
}
.ds-topbar-badge{
  background:var(--fg);color:#fff;
  font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:4px;letter-spacing:.06em;
}
.ds-topbar-right{font-size:0.78rem;color:var(--muted);text-decoration:none!important;}
.ds-topbar-right:hover{color:#111827!important;}
.ds-stepbar{
  display:flex;align-items:center;gap:4px;flex-wrap:wrap;
  margin-bottom:28px;padding:10px 0;border-bottom:1px solid var(--border);
}
.ds-step{border-radius:4px;padding:3px 12px;font-size:0.78rem;font-weight:500;white-space:nowrap;}
.ds-step-done{color:var(--muted);}
.ds-step-active{background:var(--fg);color:#fff;font-weight:600;}
.ds-step-locked,.ds-step-optional{color:#d1d5db;}
.ds-step-arrow{color:#d1d5db;font-size:0.85rem;padding:0 1px;}
.ds-divider{border:none;border-top:1px solid var(--border);margin:20px 0;}
.ds-page{display:contents;}
[data-testid="stMetric"]{
  background:var(--bg)!important;border:1px solid var(--border)!important;
  border-radius:var(--radius)!important;padding:14px 18px!important;
}
.stButton>button{
  width:auto!important;padding:5px 16px!important;border-radius:var(--radius)!important;
  font-size:0.82rem!important;font-weight:500!important;
}
.stButton>button[kind="primary"]{
  background:var(--fg)!important;border:1px solid var(--fg)!important;
  color:#fff!important;font-weight:600!important;
}
.stButton>button[kind="secondary"]{
  background:#fff!important;border:1px solid var(--border)!important;color:var(--fg)!important;
}
.risk-badge{
  display:inline-block;padding:6px 20px;border-radius:6px;
  font-size:1rem;font-weight:700;letter-spacing:.03em;margin-top:4px;
}
.risk-low{background:#dcfce7;color:#166534;}
.risk-med{background:#fef9c3;color:#854d0e;}
.risk-high{background:#fee2e2;color:#991b1b;}
</style>
""", unsafe_allow_html=True)

# ── Topbar ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="ds-topbar">'
    '<a class="ds-topbar-logo" href="/" target="_self">'
    '<span style="font-family:\'Material Symbols Outlined\';font-size:1.2rem">local_hospital</span>'
    'DataSUS AI<span class="ds-topbar-badge">PREDICTION</span>'
    '</a>'
    '<a class="ds-topbar-right" href="/" target="_self">Inferência Individual</a>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Session state ──────────────────────────────────────────────────────────────
ss = st.session_state

# ── Guard ──────────────────────────────────────────────────────────────────────
if not ss.get("model_results") or not ss.get("outcome_key") or ss.get("cohort") is None:
    st.warning("Nenhum modelo treinado encontrado. Volte para a etapa de treinamento.")
    if st.button("← Voltar ao Pipeline"):
        st.switch_page("pages/analise.py")
    st.stop()

# ── Step bar ───────────────────────────────────────────────────────────────────
labels = ["Desfecho", "Dados", "Features", "Tratamento", "Modelo", "Treinamento", "Resultados", "Calibração", "Benchmark", "Deploy"]
optionals = {8, 9, 10}
parts = []
for i, lbl in enumerate(labels, 1):
    optional = i in optionals
    cls = ("ds-step ds-step-done" if i < 10
           else "ds-step ds-step-active" if i == 10
           else "ds-step ds-step-optional")
    dot = "✓" if i < 10 else str(i)
    suffix = " *" if optional else ""
    parts.append(f'<span class="{cls}">{dot}. {lbl}{suffix}</span>')
    if i < len(labels):
        parts.append('<span class="ds-step-arrow">›</span>')
st.markdown('<div class="ds-stepbar">' + "".join(parts) + "</div>", unsafe_allow_html=True)
st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

if st.button("← Voltar", type="secondary"):
    st.switch_page("pages/analise.py")

st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── Lazy imports ───────────────────────────────────────────────────────────────
pd = _pd()
ev = _ev()
CohortBuilder = _cohort()

from core.features.data_dict import get_info as _dd_info

outcome   = OUTCOMES[ss["outcome_key"]]
results   = ss["model_results"]
treatment = ss.get("treatment_config") or {}
cohort    = ss["cohort"]

# Usa modelo calibrado se disponível
_calib = ss.get("calib_results") or {}
model = _calib.get("cal_model") or results["model"]

feature_cols = results["X_columns"]
builder = CohortBuilder(outcome)
X_train, y_train = builder.get_Xy(cohort)
X_res = X_train[feature_cols]

num_cols = treatment.get("num_cols", X_res.select_dtypes(include="number").columns.tolist())
cat_cols = treatment.get("cat_cols", X_res.select_dtypes(exclude="number").columns.tolist())

# ── Título ────────────────────────────────────────────────────────────────────
st.markdown("## Passo 10 — Deploy — Inferência Individual")
st.caption(
    f"Preencha os valores de um paciente e clique em **Predizer** para obter "
    f"a probabilidade de **{outcome.name}** com explicação SHAP individual."
)
st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── Formulário de entrada ─────────────────────────────────────────────────────
input_vals: dict = {}

with st.form("deploy_form"):
    n_num = len([c for c in feature_cols if c in num_cols])
    n_cat = len([c for c in feature_cols if c in cat_cols])

    if n_num:
        st.markdown("**Variáveis Numéricas**")
        _ncols = 3
        _num_feats = [c for c in feature_cols if c in num_cols]
        for row_start in range(0, len(_num_feats), _ncols):
            _row = _num_feats[row_start: row_start + _ncols]
            cols = st.columns(_ncols)
            for ci, col in enumerate(_row):
                info = _dd_info(col) or {}
                label = info.get("label", col)
                desc  = info.get("desc", "")
                _min  = float(X_res[col].min()) if col in X_res else 0.0
                _max  = float(X_res[col].max()) if col in X_res else 100.0
                _med  = float(X_res[col].median()) if col in X_res else (_min + _max) / 2
                input_vals[col] = cols[ci].number_input(
                    label,
                    min_value=_min,
                    max_value=_max,
                    value=_med,
                    help=desc or f"{col} · min {_min:.1f} · max {_max:.1f}",
                    key=f"inp_{col}",
                )

    if n_cat:
        st.markdown("**Variáveis Categóricas**")
        _cat_feats = [c for c in feature_cols if c in cat_cols]
        for row_start in range(0, len(_cat_feats), _ncols):
            _row = _cat_feats[row_start: row_start + _ncols]
            cols = st.columns(_ncols)
            for ci, col in enumerate(_row):
                info = _dd_info(col) or {}
                label = info.get("label", col)
                desc  = info.get("desc", "")
                _opts = sorted(X_res[col].dropna().astype(str).unique().tolist()) if col in X_res else []
                _default = _opts[0] if _opts else ""
                input_vals[col] = cols[ci].selectbox(
                    label,
                    options=_opts if _opts else ["—"],
                    help=desc or col,
                    key=f"inp_{col}",
                )

    submitted = st.form_submit_button("Predizer", type="primary", use_container_width=False)

# ── Inferência ────────────────────────────────────────────────────────────────
if submitted:
    try:
        # Monta DataFrame com os valores do usuário
        row_data = {}
        for col in feature_cols:
            val = input_vals.get(col)
            # Converte de volta para o dtype do treino
            if col in num_cols:
                row_data[col] = float(val) if val is not None else float("nan")
            else:
                row_data[col] = str(val) if val is not None else None
        input_df = pd.DataFrame([row_data], columns=feature_cols)

        # Predição
        prob = float(model.predict_proba(input_df)[0, 1])
        prevalence = float(y_train.mean())

        # Classificação de risco relativa à prevalência da coorte
        if prob < prevalence * 0.75:
            risk_label, risk_cls = "Baixo risco", "risk-low"
        elif prob < prevalence * 1.5:
            risk_label, risk_cls = "Risco moderado", "risk-med"
        else:
            risk_label, risk_cls = "Alto risco", "risk-high"

        st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
        st.markdown("### Resultado da Predição")

        # Gauge + métricas
        import plotly.graph_objects as _go
        fig_gauge = _go.Figure(_go.Indicator(
            mode="gauge+number",
            value=round(prob * 100, 1),
            number={"suffix": "%", "font": {"size": 36}},
            title={"text": f"Probabilidade de {outcome.name}", "font": {"size": 14}},
            gauge={
                "axis": {"range": [0, 100], "ticksuffix": "%"},
                "bar": {"color": "#ef4444" if prob >= prevalence * 1.5
                                else "#f97316" if prob >= prevalence * 0.75
                                else "#22c55e"},
                "steps": [
                    {"range": [0, prevalence * 75], "color": "#f0fdf4"},
                    {"range": [prevalence * 75, prevalence * 150], "color": "#fef9c3"},
                    {"range": [prevalence * 150, 100], "color": "#fee2e2"},
                ],
                "threshold": {
                    "line": {"color": "#6b7280", "width": 2},
                    "thickness": 0.75,
                    "value": prevalence * 100,
                },
            },
        ))
        fig_gauge.update_layout(height=280, margin=dict(t=40, b=0, l=30, r=30),
                                paper_bgcolor="white")

        col_g, col_m = st.columns([2, 1])
        with col_g:
            st.plotly_chart(fig_gauge, use_container_width=True)
        with col_m:
            st.metric("Probabilidade predita", f"{prob:.1%}")
            st.metric("Prevalência da coorte", f"{prevalence:.1%}")
            st.metric("Razão risco/prevalência", f"{prob/prevalence:.2f}x")
            st.markdown(
                f'<span class="risk-badge {risk_cls}">{risk_label}</span>',
                unsafe_allow_html=True,
            )

        # SHAP individual
        st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
        st.markdown("### Explicação SHAP — Contribuição de cada variável")
        st.caption(
            "Vermelho = variável aumenta o risco · Azul = variável reduz o risco · "
            "Comprimento = magnitude da contribuição"
        )
        with st.spinner("Calculando SHAP…"):
            shap_fig = ev.shap_waterfall_chart(model, input_df, case_idx=0)
        if shap_fig:
            shap_fig.update_layout(
                title=f"SHAP — {outcome.name} · Score {prob:.3f}",
                height=max(380, len(feature_cols) * 26),
            )
            st.plotly_chart(shap_fig, use_container_width=True)
        else:
            st.info("SHAP indisponível para este algoritmo (ex: Logistic Regression requer dados de fundo).")

        # Tabela de valores inseridos
        with st.expander("Valores inseridos para esta predição"):
            _display = pd.DataFrame([{
                (_dd_info(c) or {}).get("label", c): input_df[c].iloc[0]
                for c in feature_cols
            }]).T.rename(columns={0: "Valor"})
            st.dataframe(_display, use_container_width=True)

    except Exception as e:
        st.error(f"Erro na predição: {e}")
        st.exception(e)
