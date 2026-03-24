"""DataSUS AI Prediction — Calibracao e Benchmark (pagina separada)."""
from __future__ import annotations
from pathlib import Path
from PIL import Image as _PILImage

import streamlit as st
from core.outcomes import OUTCOMES

# ── Lazy loaders ───────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _dl():
    from core.data.downloader import STATES, fetch
    return STATES, fetch

@st.cache_resource(show_spinner=False)
def _cohort():
    from core.features.cohort import CohortBuilder
    return CohortBuilder

@st.cache_resource(show_spinner=False)
def _pipeline():
    from core.models.pipeline import calibrate_model, build_pipeline
    return calibrate_model, build_pipeline

@st.cache_resource(show_spinner=False)
def _ev():
    from core.models import evaluation
    return evaluation

@st.cache_resource(show_spinner=False)
def _pd():
    import pandas as pd
    return pd

@st.cache_resource(show_spinner=False)
def _px():
    import plotly.express as px
    return px


_favicon = _PILImage.open(Path(__file__).parent.parent / "favicon.png")
st.set_page_config(
    page_title="DataSUS AI — Calibração",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS + topbar (shared design system) ───────────────────────────────────────
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
  font-size: 0.78rem; color: #111827; font-weight: 500;
  text-decoration: none !important;
  display: flex; align-items: center; gap: 5px;
}
.ds-topbar-right:hover { opacity: 0.7; }
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
.ds-done-bar {
  background: var(--done-bg); border: 1px solid var(--done-border);
  border-radius: var(--radius); padding: 9px 14px; margin-bottom: 4px;
}
.ds-done-label { font-size: 0.84rem; color: var(--done-fg); }
.ds-section-title { font-size: 1rem; font-weight: 700; color: var(--fg); margin: 0 0 3px; }
.ds-section-caption { font-size: 0.8rem; color: var(--muted); margin: 0 0 16px; }
.ds-divider { border: none; border-top: 1px solid var(--border); margin: 20px 0; }
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
[data-testid="stInfo"], [data-testid="stWarning"],
[data-testid="stSuccess"] { border-radius: var(--radius) !important; }
.ds-info-box {
  background: #f9fafb !important; border: 1px solid #e5e7eb !important;
  border-radius: var(--radius) !important; padding: 12px 16px !important;
  margin: 4px 0 12px !important; font-size: 0.85rem !important;
  color: #374151 !important; line-height: 1.5 !important;
}
.ds-info-box * { color: #374151 !important; }
.ds-warn-box {
  background: #f9fafb !important; border: 1px solid #e5e7eb !important;
  border-left: 3px solid #d1d5db !important; border-radius: var(--radius) !important;
  padding: 12px 16px !important; margin: 4px 0 12px !important;
  font-size: 0.85rem !important; color: #374151 !important; line-height: 1.5 !important;
}
.ds-warn-box * { color: #374151 !important; }
[data-testid="stExpander"] {
  background: var(--bg) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; box-shadow: none !important;
}
.ds-page { display: contents; }
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
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
ss = st.session_state
_defaults: dict = {
    "outcome_key": None, "raw_data": {}, "cohort": None,
    "model_results": None, "calib_results": None, "comparison_results": [],
    "sel_states": ["SP"], "sel_years": [2023], "manual_needed": [],
    "sample_n": 10_000, "sample_seed": 42, "use_sample": True,
    "show_benchmark": False,
}
for k, v in _defaults.items():
    if k not in ss:
        ss[k] = v


# ── Helpers ────────────────────────────────────────────────────────────────────
def render_topbar() -> None:
    st.markdown(
        '<div class="ds-topbar">'
        '<a class="ds-topbar-logo" href="/" target="_self">'
        '<span class="ms" style="font-size:1.2rem;color:#111827">local_hospital</span>'
        'DataSUS AI'
        '<span class="ds-topbar-badge">PREDICTION</span>'
        '</a>'
        '<a class="ds-topbar-right" href="/" target="_self">'
        '<span class="ms">leaderboard</span>Benchmark entre Estados'
        '</a>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_step_bar(step: int) -> None:
    labels = ["Desfecho", "Dados", "Features", "Tratamento", "Modelo", "Treinamento", "Resultados", "Benchmark", "Deploy", "Relatório"]
    optionals = {8, 9, 10}
    parts = []
    for i, lbl in enumerate(labels, 1):
        optional = i in optionals
        if i < step:
            cls = "ds-step ds-step-done"
            dot = "✓"
        elif i == step:
            cls = "ds-step ds-step-active"
            dot = str(i)
        elif optional:
            cls = "ds-step ds-step-optional"
            dot = str(i)
        else:
            cls = "ds-step ds-step-locked"
            dot = str(i)
        suffix = " *" if optional else ""
        parts.append(f'<span class="{cls}">{dot}. {lbl}{suffix}</span>')
        if i < len(labels):
            parts.append('<span class="ds-step-arrow">›</span>')
    st.markdown('<div class="ds-stepbar">' + "".join(parts) + "</div>", unsafe_allow_html=True)


def done_bar(text: str, change_key: str, reset_keys: list[str]) -> None:
    col1, col2 = st.columns([10, 1])
    with col1:
        st.markdown(
            f'<div class="ds-done-bar"><span class="ds-done-label">{text}</span></div>',
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("Editar", key=change_key, help="Alterar"):
            for k in reset_keys:
                ss[k] = _defaults[k]
            ss["show_benchmark"] = False
            st.rerun()


def step_title(n: int, title: str, caption: str = "") -> None:
    st.markdown(
        f'<p class="ds-section-title">Passo {n} — {title}</p>'
        + (f'<p class="ds-section-caption">{caption}</p>' if caption else ""),
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
            _n_f = len(ss["feature_config"].get("selected_features", []))
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">4 · Features</div>'
                f'<div class="sb-step-value">{_n_f} variáveis</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if ss.get("treatment_config"):
            tc_ = ss["treatment_config"]
            _num_lbl = {"none": "Sem escala", "standard": "Z-score", "minmax": "Min-Max"}.get(
                tc_.get("num_default", "none"), "—")
            _cat_lbl = {"none": "Sem trat.", "ohe": "One-Hot", "ordinal": "Ordinal", "target": "Target", "drop": "Remover"}.get(
                tc_.get("cat_default", "none"), "—")
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">5 · Tratamento</div>'
                f'<div class="sb-step-value">Num: {_num_lbl} · Cat: {_cat_lbl}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if ss.get("model_config"):
            cfg_ = ss["model_config"]
            _vs = (
                f"{cfg_['n_folds']}-fold CV"
                if cfg_["val_strategy"] == "Validação cruzada (k-fold)"
                else f"Holdout {cfg_['holdout_size']:.0%}"
            )
            _albl = " · ".join(cfg_.get("algo_labels", [cfg_["algo_label"]]))
            _fc_ = ss.get("feature_config") or {}
            _nf = len(_fc_.get("selected_features", []))
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">6 · Modelo</div>'
                f'<div class="sb-step-value">{_albl}<br>'
                f'<span style="font-size:.7rem;color:#6b7280">{_vs} · {_nf} feat.</span></div>'
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


# ── Topbar ─────────────────────────────────────────────────────────────────────
render_topbar()
render_sidebar()
st.markdown('<div class="ds-page">', unsafe_allow_html=True)

# ── Guard: precisa ter modelo treinado ─────────────────────────────────────────
if not ss["model_results"] or not ss["outcome_key"] or ss["cohort"] is None:
    st.warning("Nenhum modelo treinado encontrado. Volte para a etapa de treinamento.")
    if st.button("← Voltar ao Modelo", type="primary"):
        st.switch_page("pages/analise.py")
    st.stop()

# ── Botão de retorno (acima do step bar, igual ao Relatório) ───────────────────
if st.button("Resultados", icon=":material/arrow_back:", type="secondary"):
    st.switch_page("pages/analise.py")

# ── Stepbar ────────────────────────────────────────────────────────────────────
_step = 8  # Benchmark é agora o passo 8
render_step_bar(_step)

# ── Lazy modules ───────────────────────────────────────────────────────────────
pd = _pd()
px = _px()
ev = _ev()
calibrate_model, build_pipeline = _pipeline()
STATES, fetch = _dl()
CohortBuilder = _cohort()

outcome = OUTCOMES[ss["outcome_key"]]
cohort = ss["cohort"]
results = ss["model_results"]

builder = CohortBuilder(outcome)
X, y = builder.get_Xy(cohort)
X_res = X[results["X_columns"]]

# ── Modelo ativo (calibrado se disponível) ─────────────────────────────────────
_active_model = results["model"]
if ss.get("calib_results") and not ss["calib_results"].get("skipped"):
    _active_model = ss["calib_results"]["cal_model"]

# ── Calibração: feita inline na aba Resultados (passo 7). Auto-skip se não feita. ──
if not ss.get("calib_results"):
    ss["calib_results"] = {"skipped": True, "cal_model": results["model"]}

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 8 — BENCHMARK ENTRE ESTADOS (opcional) — só aparece quando ativado
# ═════════════════════════════════════════════════════════════════════════════

# Se benchmark não ativado nem tem resultados, mostrar só o botão de acesso
if not ss.get("show_benchmark") and not ss.get("comparison_results"):
    _bm_l, _bm_spacer, _bm_r = st.columns([3, 3, 2])
    with _bm_r:
        if st.button("→ Benchmark entre Estados", type="secondary", use_container_width=True):
            ss["show_benchmark"] = True
            st.rerun()
    st.stop()

_bm_title_col, _bm_gap_col, _bm_btn_col = st.columns([3, 1, 1])
with _bm_title_col:
    step_title(8, "Benchmark entre Estados",
               "Replica o pipeline em diferentes estados e compara curva ROC e importância das features.")
with _bm_btn_col:
    st.markdown("<div style='padding-top:4px'>", unsafe_allow_html=True)
    if st.button("Relatório Final", key="btn_relatorio_top", icon=":material/summarize:", type="primary", use_container_width=True):
        st.switch_page("pages/relatorio.py")
    st.markdown("</div>", unsafe_allow_html=True)

if ss["comparison_results"]:
    import plotly.graph_objects as go
    import numpy as np
    from sklearn.metrics import roc_curve

    comp = ss["comparison_results"]
    st.markdown("**Métricas por coorte**")
    st.dataframe(ev.metrics_comparison_table(comp), use_container_width=True, hide_index=True)

    # ── ROC Overlay ──────────────────────────────────────────────────────────
    _colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
               "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    roc_valid = [r for r in comp if r.get("oof_probs") is not None and r.get("y_true") is not None]
    if roc_valid:
        st.markdown("**Curva ROC por estado**")
        fig_roc = go.Figure()
        fig_roc.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1], mode="lines", name="Aleatório",
            line=dict(dash="dash", color="lightgray"), showlegend=True,
        ))
        for i, r in enumerate(roc_valid):
            _fpr, _tpr, _ = roc_curve(r["y_true"], r["oof_probs"])
            try:
                _auc = float(np.trapezoid(_tpr, _fpr))
            except AttributeError:
                _auc = float(np.trapz(_tpr, _fpr))
            fig_roc.add_trace(go.Scatter(
                x=_fpr, y=_tpr, mode="lines",
                name=f"{r['label']} (AUC={_auc:.3f})",
                line=dict(color=_colors[i % len(_colors)], width=2),
            ))
        fig_roc.update_layout(
            xaxis_title="Taxa de Falsos Positivos",
            yaxis_title="Taxa de Verdadeiros Positivos",
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_roc, use_container_width=True)

    # ── Feature Importance Comparison ────────────────────────────────────────
    fi_valid = [r for r in comp if r.get("feature_importances")]
    if fi_valid:
        st.markdown("**Importância das features por estado**")
        # Top features by mean importance across states
        all_feats = set()
        for r in fi_valid:
            all_feats.update(r["feature_importances"].keys())
        _mean_imp = {
            f: np.mean([r["feature_importances"].get(f, 0) for r in fi_valid])
            for f in all_feats
        }
        top_feats = sorted(_mean_imp, key=lambda f: _mean_imp[f], reverse=True)[:15]

        fig_fi = go.Figure()
        for i, r in enumerate(fi_valid):
            vals = [r["feature_importances"].get(f, 0) for f in top_feats]
            fig_fi.add_trace(go.Bar(
                name=r["label"],
                x=top_feats,
                y=vals,
                marker_color=_colors[i % len(_colors)],
            ))
        fig_fi.update_layout(
            barmode="group",
            xaxis_tickangle=-35,
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_fi, use_container_width=True)

    if st.button("Limpar e comparar outros estados", type="secondary"):
        ss["comparison_results"] = []
        ss["show_benchmark"] = True
        st.rerun()
else:
    st.markdown(
        '<div class="ds-info-box">Selecione estados adicionais para comparar o '
        'desempenho do modelo treinado em populações diferentes.</div>',
        unsafe_allow_html=True,
    )
    cmp_col1, cmp_col2 = st.columns(2)
    with cmp_col1:
        already_used = ss["sel_states"]
        _cmp_options = [s for s in STATES if s not in already_used]
        cmp_states = st.multiselect(
            "Estados para comparação",
            _cmp_options,
            default=["ES"] if "ES" in _cmp_options else [],
            help="Baixa os dados, constrói a coorte e aplica o modelo treinado.",
        )
        include_original = st.checkbox(
            f"Incluir coorte original ({', '.join(already_used)})", value=True,
        )
    with cmp_col2:
        cmp_years = st.multiselect("Anos", list(range(2018, 2025)), default=ss["sel_years"])

    if not cmp_states and not include_original:
        st.warning("Selecione pelo menos um estado ou mantenha a coorte original.")
    elif st.button("Rodar comparação", type="primary"):
        comp_list = []

        # ── Config do pipeline original (reutilizada em cada estado) ──────────
        from core.models.pipeline import train_cv as _train_cv
        _algo       = results.get("algorithm", ss.get("model_config", {}).get("algo", "rf"))
        _params     = results.get("best_params", {}) or {}
        _n_folds    = ss.get("model_config", {}).get("n_folds", 5)
        _balancing  = ss.get("model_config", {}).get("balancing", "none")
        _treatment  = ss.get("treatment_config")       # mesmo tratamento do treino original
        _train_cols = results["X_columns"]
        _train_n    = results.get("sample_n")

        def _run_state_group(label: str, states: list[str], years: list[int], raw_override=None):
            """Replica o pipeline completo (fit + CV) no estado/grupo indicado.

            Cada grupo roda train_cv com a mesma configuração do modelo original
            (algoritmo, hiperparâmetros, tratamento, n_folds, balanceamento),
            garantindo comparação homogênea entre estados — sem depender de
            transferência do modelo treinado em SP.
            """
            try:
                # ── Coorte original: reutiliza métricas e OOF probs já calculadas ──
                if raw_override is not None:
                    _oof = results.get("oof_probs")
                    # holdout/temporal: results["y_eval"] guarda apenas o subset de teste
                    # CV: oof_probs cobre todo o conjunto de treino (mesmo len que cohort y)
                    _y_true = results.get("y_eval")
                    if _y_true is None and _oof is not None and len(y) == len(_oof):
                        _y_true = y.values
                    return {
                        "label": label,
                        "n": _train_n or len(X_res),
                        "metrics": results["mean_metrics"],
                        "oof_probs": _oof,
                        "y_true": _y_true,
                        "feature_importances": results.get("feature_importances", {}),
                    }

                # ── Estados de comparação: baixa dados e re-treina do zero ────
                raw = {}
                for src in outcome.data_sources:
                    dfs = []
                    for st_ in states:
                        for yr in years:
                            dfs.append(fetch(src, st_, yr))
                    raw[src] = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

                builder_cmp = CohortBuilder(outcome)
                cohort_cmp  = builder_cmp.build(raw)
                X_cmp, y_cmp = builder_cmp.get_Xy(cohort_cmp)

                # Alinha features ao mesmo conjunto do treino original
                for col in _train_cols:
                    if col not in X_cmp.columns:
                        X_cmp[col] = float("nan")
                X_cmp = X_cmp[_train_cols]

                # Limita ao mesmo N para comparação justa
                if _train_n and len(X_cmp) > _train_n:
                    _idx = X_cmp.sample(n=_train_n, random_state=42).index
                    X_cmp  = X_cmp.loc[_idx]
                    y_cmp  = y_cmp.loc[_idx]

                if len(y_cmp) < 20 or y_cmp.nunique() < 2:
                    st.warning(f"{label}: dados insuficientes ou sem variação no desfecho — ignorado.")
                    return None

                # ── Treina pipeline com mesma config — banana com banana ──────
                _cmp_r = _train_cv(
                    X_cmp, y_cmp,
                    algorithm=_algo,
                    params=_params,
                    n_folds=_n_folds,
                    balancing=_balancing,
                    treatment=_treatment,
                )

                return {
                    "label": label,
                    "n": len(y_cmp),
                    "metrics": _cmp_r["mean_metrics"],
                    "oof_probs": _cmp_r["oof_probs"],
                    "y_true": y_cmp.values,
                    "feature_importances": _cmp_r.get("feature_importances", {}),
                }

            except Exception as exc:
                st.error(f"Erro em {label}: {exc}")
                return None

        prog_cmp = st.progress(0.0, text="Iniciando comparação…")
        all_groups = []
        if include_original:
            all_groups.append(
                (f"{'+'.join(already_used)} · {'+'.join(map(str, ss['sel_years']))}",
                 already_used, ss["sel_years"], ss["raw_data"])
            )
        for st_ in cmp_states:
            all_groups.append(
                (f"{st_} · {'+'.join(map(str, cmp_years))}", [st_], cmp_years, None)
            )

        for idx, (lbl, sts, yrs, raw_ov) in enumerate(all_groups):
            prog_cmp.progress(idx / len(all_groups), text=f"Processando {lbl}…")
            r = _run_state_group(lbl, sts, yrs, raw_ov)
            if r:
                comp_list.append(r)

        prog_cmp.progress(1.0, text="Comparação concluída.")
        ss["comparison_results"] = comp_list
        st.rerun()


st.markdown('</div>', unsafe_allow_html=True)
