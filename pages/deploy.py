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
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,300,0,0" />

<style>
:root {
  --primary: #111827; --primary-hover: #374151;
  --primary-light: #f3f4f6; --primary-ring: rgba(17,24,39,.12);
  --bg: #ffffff; --bg-page: #ffffff;
  --fg: #111827; --muted: #6b7280; --border: #e5e7eb;
  --done-bg: #f9fafb; --done-border: #e5e7eb; --done-fg: #374151;
  --radius: 6px; --topbar-h: 52px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,.05);
}
.ms {
  font-family: 'Material Symbols Outlined';
  font-style: normal; font-weight: normal;
  font-size: 1rem; line-height: 1;
  vertical-align: middle; display: inline-block;
  color: var(--fg);
}
header, footer,
[data-testid="stSidebarNav"], [data-testid="stHeader"],
[data-testid="stToolbar"], [data-testid="stDecoration"],
#MainMenu { display: none !important; }

html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif !important;
  color: var(--fg) !important;
}
.block-container {
  padding-top: calc(var(--topbar-h) + 32px) !important;
  padding-bottom: 56px !important;
  padding-left: 40px !important; padding-right: 40px !important;
  max-width: 1100px !important;
}
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {
  position: fixed !important;
  top: 0 !important; left: 0 !important;
  height: var(--topbar-h) !important; width: 52px !important;
  z-index: 10001 !important;
  background: #ffffff !important; border: none !important;
  border-right: 1px solid #e5e7eb !important;
  display: flex !important; align-items: center !important;
  justify-content: center !important; cursor: pointer !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg {
  color: #111827 !important; fill: #111827 !important;
  width: 18px !important; height: 18px !important;
}
[data-testid="stSidebar"] {
  top: var(--topbar-h) !important;
  height: calc(100vh - var(--topbar-h)) !important;
  background: #ffffff !important; border-right: 1px solid #e5e7eb !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 1.25rem 1rem 1rem !important;
  height: 100% !important; overflow-y: auto !important;
}
.ds-topbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  height: var(--topbar-h); background: var(--bg);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 48px 0 calc(52px + 20px);
}
.ds-topbar-logo {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.93rem; font-weight: 700;
  color: #111827 !important; text-decoration: none !important;
}
.ds-topbar-badge {
  background: var(--fg); color: #fff;
  font-size: 0.62rem; font-weight: 700;
  padding: 2px 7px; border-radius: 4px; letter-spacing: .06em;
}
.ds-topbar-right {
  font-size: 0.78rem; color: var(--muted);
  text-decoration: none !important;
}
.ds-topbar-right:hover { color: #111827 !important; }
.ds-stepbar {
  display: flex; align-items: center; gap: 2px; flex-wrap: nowrap;
  overflow-x: auto; scrollbar-width: none;
  margin-bottom: 28px; padding: 10px 0; border-bottom: 1px solid var(--border);
}
.ds-stepbar::-webkit-scrollbar { display: none; }
.ds-step {
  border-radius: 4px; padding: 2px 7px;
  font-size: 0.7rem; font-weight: 500; white-space: nowrap; flex-shrink: 0;
}
.ds-step-done   { color: var(--muted); }
.ds-step-active { background: var(--fg); color: #fff; font-weight: 600; }
.ds-step-locked { color: #d1d5db; }
.ds-step-optional { color: #d1d5db; }
.ds-step-arrow  { color: #d1d5db; font-size: 0.75rem; padding: 0; flex-shrink: 0; }
.ds-divider { border: none; border-top: 1px solid var(--border); margin: 20px 0; }
.ds-page { display: contents; }
[data-testid="stMetric"] {
  background: var(--bg) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; padding: 14px 18px !important;
  box-shadow: none !important;
}
.stButton { display: flex !important; justify-content: flex-start !important; }
.stButton > button {
  width: auto !important; min-width: 0 !important; padding: 5px 16px !important;
  border-radius: var(--radius) !important; font-size: 0.82rem !important;
  font-weight: 500 !important; transition: all .12s !important;
  cursor: pointer !important; white-space: nowrap !important;
}
.stButton > button[kind="primary"] {
  background: var(--fg) !important; border: 1px solid var(--fg) !important;
  color: #fff !important; font-weight: 600 !important; box-shadow: none !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--primary-hover) !important; border-color: var(--primary-hover) !important;
}
.stButton > button[kind="secondary"] {
  background: #fff !important; border: 1px solid var(--border) !important;
  color: var(--fg) !important; box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: var(--fg) !important; background: var(--primary-light) !important;
}
[data-testid="stExpander"] {
  background: var(--bg) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; box-shadow: none !important;
}
.sb-title {
  font-size: .65rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .1em; color: #6b7280; margin-bottom: 10px;
  padding-bottom: 6px; border-bottom: 1px solid #e5e7eb;
}
.sb-step {
  padding: 8px 10px; margin-bottom: 5px;
  border: 1px solid #e5e7eb; border-radius: 6px; background: #f9fafb;
}
.sb-step-label {
  font-size: .6rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .08em; color: #6b7280; margin-bottom: 2px;
}
.sb-step-value { font-size: .78rem; color: #111827; font-weight: 500; line-height: 1.35; }
.risk-badge {
  display: inline-block; padding: 6px 20px; border-radius: 6px;
  font-size: 1rem; font-weight: 700; letter-spacing: .03em; margin-top: 4px;
}
.risk-low  { background: #dcfce7; color: #166534; }
.risk-med  { background: #fef9c3; color: #854d0e; }
.risk-high { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# ── Session state ───────────────────────────────────────────────────────────────
ss = st.session_state


# ── Helpers ────────────────────────────────────────────────────────────────────
def render_topbar() -> None:
    st.markdown(
        '<div class="ds-topbar">'
        '<a class="ds-topbar-logo" href="/" target="_self">'
        '<span class="ms" style="font-size:1.2rem;color:#111827">local_hospital</span>'
        'DataSUS AI'
        '<span class="ds-topbar-badge">PREDICTION</span>'
        '</a>'
        '<a class="ds-topbar-right" href="/" target="_self">Inferência Individual</a>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_step_bar() -> None:
    labels = ["Desfecho", "Dados", "Features", "Tratamento", "Modelo",
              "Treinamento", "Resultados", "Benchmark", "Deploy", "Relatório"]
    optionals = {8, 9, 10}
    parts = []
    for i, lbl in enumerate(labels, 1):
        optional = i in optionals
        if i < 9:
            cls = "ds-step ds-step-done"
            dot = "✓"
        elif i == 9:
            cls = "ds-step ds-step-active"
            dot = "9"
        else:
            cls = "ds-step ds-step-optional"
            dot = str(i)
        suffix = " *" if optional else ""
        parts.append(f'<span class="{cls}">{dot}. {lbl}{suffix}</span>')
        if i < len(labels):
            parts.append('<span class="ds-step-arrow">›</span>')
    st.markdown(
        '<div class="ds-stepbar">'
        + "".join(parts)
        + '<span style="margin-left:auto;font-size:0.65rem;color:#9ca3af;white-space:nowrap;flex-shrink:0;">* etapa opcional</span>'
        + "</div>",
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown('<p class="sb-title">Pipeline</p>', unsafe_allow_html=True)

        if ss.get("outcome_key"):
            o = OUTCOMES[ss["outcome_key"]]
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">1 · Desfecho</div>'
                f'<div class="sb-step-value">{o.name}<br>'
                f'<span style="font-size:.7rem;color:#6b7280">{", ".join(o.data_sources)}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if ss.get("raw_data"):
            lines = "<br>".join(f"{src}: {len(df):,}" for src, df in ss["raw_data"].items())
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">2 · Dados</div>'
                f'<div class="sb-step-value">{lines}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if ss.get("cohort") is not None:
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">3 · Coorte</div>'
                f'<div class="sb-step-value">{len(ss["cohort"]):,} registros</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if ss.get("feature_config"):
            fc = ss["feature_config"]
            n_feat = len(fc.get("selected_features", []))
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">4 · Features</div>'
                f'<div class="sb-step-value">{n_feat} variáveis</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if ss.get("treatment_config"):
            tc = ss["treatment_config"]
            num_m = tc.get("num_strategy", "—")
            cat_m = tc.get("cat_strategy", "—")
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">5 · Tratamento</div>'
                f'<div class="sb-step-value">Num: {num_m} · Cat: {cat_m}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if ss.get("model_config"):
            mc = ss["model_config"]
            algo_lbl = mc.get("algo_label", mc.get("algorithm", "?").upper())
            val_tag = mc.get("val_tag_label", "")
            n_feat = len(mc.get("selected_features", []))
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">6 · Modelo</div>'
                f'<div class="sb-step-value">{algo_lbl}<br>'
                f'<span style="font-size:.7rem;color:#6b7280">{val_tag} · {n_feat} feat.</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if ss.get("model_results"):
            r_ = ss["model_results"]
            m_ = r_["mean_metrics"]
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">7 · Treinamento</div>'
                f'<div class="sb-step-value">AUC {m_["roc_auc"]:.3f} · F1 {m_["f1"]:.3f}<br>'
                f'<span style="font-size:.7rem;color:#6b7280">PR-AUC {m_["pr_auc"]:.3f}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if ss.get("calib_results") and not ss["calib_results"].get("skipped"):
            cr_ = ss["calib_results"]
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">8 · Calibração</div>'
                f'<div class="sb-step-value">{cr_["method"].capitalize()}<br>'
                f'<span style="font-size:.7rem;color:#6b7280">Brier {cr_["brier_after"]:.4f}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ── Topbar + sidebar ───────────────────────────────────────────────────────────
render_topbar()
render_sidebar()
st.markdown('<div class="ds-page">', unsafe_allow_html=True)

# ── Guard ──────────────────────────────────────────────────────────────────────
if not ss.get("model_results") or not ss.get("outcome_key") or ss.get("cohort") is None:
    st.warning("Nenhum modelo treinado encontrado. Volte para a etapa de treinamento.")
    if st.button("← Voltar ao Pipeline", type="primary"):
        st.switch_page("pages/analise.py")
    st.stop()

# ── Voltar (acima do step bar) ─────────────────────────────────────────────────
if st.button("← Voltar à Calibração", type="secondary"):
    st.switch_page("pages/calibracao.py")

# ── Step bar ───────────────────────────────────────────────────────────────────
render_step_bar()

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

# ── Título ─────────────────────────────────────────────────────────────────────
st.markdown("**Passo 10 — Deploy — Inferência Individual**")
st.caption(
    f"Preencha os valores de um paciente e clique em **Predizer** para obter "
    f"a probabilidade de **{outcome.name}** com explicação SHAP individual."
)
st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── Helper: cria format_func para selectbox categórico ────────────────────────
def _make_fmt(vals_dict: dict):
    """Retorna função de formatação para st.selectbox sem closure em loop."""
    def _fmt(v: str) -> str:
        try:
            k = v.split(".")[0] if "." in v and v.endswith(".0") else v
            lbl = vals_dict.get(k) or vals_dict.get(v)
            return f"{lbl} ({v})" if lbl else v
        except Exception:
            return str(v)
    return _fmt


# ── Formulário de entrada ──────────────────────────────────────────────────────
input_vals: dict = {}
_ncols = 3

with st.form("deploy_form"):
    n_num = len([c for c in feature_cols if c in num_cols])
    n_cat = len([c for c in feature_cols if c in cat_cols])

    if n_num:
        st.markdown("**Variáveis Numéricas**")
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
                _opts = (
                    sorted(X_res[col].dropna().astype(str).unique().tolist())
                    if col in X_res else []
                )
                _vals = info.get("values", {}) if info else {}
                _fmt  = _make_fmt(_vals) if _vals else str
                input_vals[col] = cols[ci].selectbox(
                    label,
                    options=_opts if _opts else ["—"],
                    format_func=_fmt,
                    help=desc or col,
                    key=f"inp_{col}",
                )

    submitted = st.form_submit_button("Predizer", type="primary", use_container_width=False)

# ── Inferência ─────────────────────────────────────────────────────────────────
if submitted:
    try:
        # Monta DataFrame com os valores do usuário
        row_data = {}
        for col in feature_cols:
            val = input_vals.get(col)
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
            st.info("SHAP indisponível para este algoritmo.")

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

# ── Navegação para Relatório ────────────────────────────────────────────────
st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
_rel_l, _rel_r = st.columns([4, 2])
with _rel_r:
    if st.button("→ Relatório Final", type="secondary", use_container_width=True):
        st.switch_page("pages/relatorio.py")
