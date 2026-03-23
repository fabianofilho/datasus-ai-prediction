"""DataSUS AI Prediction — wizard completo (carregado sob demanda)."""
from __future__ import annotations
from pathlib import Path
from PIL import Image as _PILImage

import streamlit as st

from core.outcomes import OUTCOME_GROUPS, OUTCOMES


# ── Lazy loaders ──────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _dl():
    from core.data.downloader import STATES, ManualUploadRequired, fetch, load_from_csv
    return STATES, ManualUploadRequired, fetch, load_from_csv

@st.cache_resource(show_spinner=False)
def _cohort():
    from core.features.cohort import CohortBuilder
    return CohortBuilder

@st.cache_resource(show_spinner=False)
def _pipeline():
    from core.models.pipeline import (
        ALGORITHMS, train_cv, optimize_hyperparams, calibrate_model,
        build_pipeline, random_search, grid_search,
    )
    return ALGORITHMS, train_cv, optimize_hyperparams, calibrate_model, build_pipeline, random_search, grid_search

@st.cache_resource(show_spinner=False)
def _ev():
    from core.models import evaluation
    return evaluation

@st.cache_resource(show_spinner=False)
def _px():
    import plotly.express as px
    return px

@st.cache_resource(show_spinner=False)
def _pd():
    import pandas as pd
    return pd

_favicon = _PILImage.open(Path(__file__).parent.parent / "favicon.png")
st.set_page_config(
    page_title="DataSUS AI Prediction",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,300,0,0" />

<style>
/* ── Tokens — paleta preto/branco ────────────────────────────── */
:root {
  --primary:        #111827;
  --primary-hover:  #374151;
  --primary-light:  #f3f4f6;
  --primary-ring:   rgba(17,24,39,.12);
  --bg:             #ffffff;
  --bg-page:        #ffffff;
  --fg:             #111827;
  --muted:          #6b7280;
  --border:         #e5e7eb;
  --done-bg:        #f9fafb;
  --done-border:    #e5e7eb;
  --done-fg:        #374151;
  --radius:         6px;
  --topbar-h:       52px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,.05);
  --shadow-md: 0 2px 8px rgba(0,0,0,.08);
}

/* Material Symbols */
.ms {
  font-family: 'Material Symbols Outlined';
  font-style: normal; font-weight: normal;
  font-size: 1rem; line-height: 1;
  vertical-align: middle; display: inline-block;
  color: var(--fg);
}

/* ── Oculta elementos nativos do Streamlit ──────────────────── */
header, footer,
[data-testid="stSidebarNav"], [data-testid="stHeader"],
[data-testid="stToolbar"], [data-testid="stDecoration"],
#MainMenu { display: none !important; }

/* ── Base ───────────────────────────────────────────────────── */
html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif !important;
  color: var(--fg) !important;
}

/* ── Container ──────────────────────────────────────────────── */
.block-container {
  padding-top:    calc(var(--topbar-h) + 32px) !important;
  padding-bottom: 56px !important;
  padding-left:   40px !important;
  padding-right:  40px !important;
  max-width:      1100px !important;
}

/* ── Sidebar toggle: vive dentro da topbar (aberto e fechado) ── */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {
  position: fixed !important;
  top: 0 !important; left: 0 !important;
  height: var(--topbar-h) !important;
  width: 52px !important;
  z-index: 10001 !important;
  background: var(--bg) !important;
  border: none !important;
  border-right: 1px solid var(--border) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  cursor: pointer !important;
  color: var(--fg) !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg {
  color: var(--fg) !important;
  fill: var(--fg) !important;
  width: 18px !important; height: 18px !important;
}

/* ── Sidebar: abaixo da topbar ───────────────────────────────── */
[data-testid="stSidebar"] {
  top: var(--topbar-h) !important;
  height: calc(100vh - var(--topbar-h)) !important;
  background: var(--bg) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 0 1rem 1rem !important;
  height: 100% !important;
  overflow-y: auto !important;
}
.ds-sidebar-note {
  position: sticky; top: 0; z-index: 100;
  background: var(--bg);
  padding: 1.25rem 0 .5rem;
  font-size:.68rem; color:#6b7280; line-height:1.4;
}
.ds-sidebar-note-box {
  background:#f9fafb; border:1px solid #e5e7eb;
  border-radius:6px; padding:8px 10px;
}

/* ── Topbar ─────────────────────────────────────────────────── */
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
.ds-topbar-logo:hover { color: #374151 !important; }
.ds-topbar-badge {
  background: var(--fg); color: #fff;
  font-size: 0.62rem; font-weight: 700;
  padding: 2px 7px; border-radius: 4px;
  letter-spacing: .06em; text-transform: uppercase;
}
.ds-topbar-right {
  font-size: 0.78rem; color: var(--muted);
  text-decoration: none !important;
}
.ds-topbar-right:hover { color: var(--fg) !important; }

/* ── Step bar ───────────────────────────────────────────────── */
.ds-stepbar {
  display: flex; align-items: center; gap: 2px; flex-wrap: nowrap;
  overflow-x: auto; scrollbar-width: none;
  margin-bottom: 28px;
  padding: 10px 0; border-bottom: 1px solid var(--border);
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

/* ── Done bar ───────────────────────────────────────────────── */
.ds-done-bar {
  background: var(--done-bg); border: 1px solid var(--done-border);
  border-radius: var(--radius); padding: 9px 14px; margin-bottom: 4px;
}
.ds-done-label { font-size: 0.84rem; color: var(--done-fg); }

/* ── Section title ──────────────────────────────────────────── */
.ds-section-title {
  font-size: 1rem; font-weight: 700; color: var(--fg); margin: 0 0 3px;
}
.ds-section-caption {
  font-size: 0.8rem; color: var(--muted); margin: 0 0 16px;
}

/* ── Divisor ────────────────────────────────────────────────── */
.ds-divider { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

/* ── Métricas ───────────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--bg) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; padding: 14px 18px !important;
  box-shadow: none !important;
}
[data-testid="stMetricLabel"] {
  font-size: 0.73rem !important; color: var(--muted) !important; font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
  font-size: 1.4rem !important; font-weight: 700 !important; color: var(--fg) !important;
}

/* ── Botões ─────────────────────────────────────────────────── */
.stButton { display: flex !important; justify-content: flex-start !important; }
.stButton > button {
  width: auto !important; min-width: 0 !important;
  padding: 5px 16px !important; border-radius: var(--radius) !important;
  font-size: 0.82rem !important; font-weight: 500 !important;
  transition: all .12s !important; cursor: pointer !important;
  white-space: nowrap !important;
}
.stButton > button[kind="primary"] {
  background: var(--fg) !important; border: 1px solid var(--fg) !important;
  color: #fff !important; font-weight: 600 !important; box-shadow: none !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--primary-hover) !important; border-color: var(--primary-hover) !important;
  color: #fff !important;
}
.stButton > button[kind="secondary"] {
  background: #fff !important; border: 1px solid var(--border) !important;
  color: var(--fg) !important; box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: var(--fg) !important; color: var(--fg) !important;
  background: var(--primary-light) !important;
}

/* ── Inputs ─────────────────────────────────────────────────── */
[data-baseweb="input"], [data-baseweb="select"] > div,
[data-baseweb="base-input"] {
  background: var(--bg) !important; border-color: var(--border) !important;
  border-radius: var(--radius) !important; box-shadow: none !important;
}
[data-testid="stMultiSelect"] > div > div,
[data-testid="stSelectbox"] > div > div {
  background: var(--bg) !important; border-color: var(--border) !important;
  border-radius: var(--radius) !important; box-shadow: none !important;
}
[data-baseweb="tag"] {
  background: var(--fg) !important; border: none !important;
  border-radius: 4px !important; padding: 0 8px !important;
}
[data-baseweb="tag"] span { color: #fff !important; font-size: 0.78rem !important; }
[data-baseweb="tag"] [role="button"] svg { fill: rgba(255,255,255,.7) !important; }

/* ── Labels ─────────────────────────────────────────────────── */
[data-testid="stMultiSelect"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label,
[data-testid="stCheckbox"] label,
[data-testid="stFileUploader"] label {
  color: var(--fg) !important; font-size: 0.82rem !important; font-weight: 500 !important;
}

/* ── Banners ────────────────────────────────────────────────── */
[data-testid="stInfo"], [data-testid="stWarning"],
[data-testid="stSuccess"] { border-radius: var(--radius) !important; }

/* ── Expander ───────────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--bg) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; box-shadow: none !important;
}

/* ── Dataframe ──────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: var(--radius) !important; overflow: hidden; }

/* ── Spinner ────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div { border-color: var(--fg) !important; }

.ds-page { display: contents; }

.sb-title {
  font-size: .65rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .1em; color: var(--muted); margin-bottom: 10px;
  padding-bottom: 6px; border-bottom: 1px solid var(--border);
}
.sb-step {
  padding: 8px 10px; margin-bottom: 5px;
  border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--done-bg);
}
.sb-step-label {
  font-size: .6rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .08em; color: var(--muted); margin-bottom: 2px;
}
.sb-step-value {
  font-size: .78rem; color: var(--fg); font-weight: 500; line-height: 1.35;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
ss = st.session_state
_defaults: dict = {
    "outcome_key": None,
    "raw_data": {},
    "cohort": None,
    "feature_config": None,
    "treatment_config": None,
    "model_config": None,
    "model_results": None,
    "calib_results": None,
    "comparison_results": [],
    "sel_states": ["SP"],
    "sel_years": [2023],
    "manual_needed": [],
    "sample_n": 1_000,
    "sample_seed": 42,
}
for k, v in _defaults.items():
    if k not in ss:
        ss[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────────
def current_step() -> int:
    if ss.get("comparison_results"):
        return 9
    if ss.get("calib_results"):
        return 8
    if ss["model_results"]:
        return 7
    if ss.get("model_config"):
        return 6
    if ss.get("treatment_config"):
        return 5
    if ss.get("feature_config"):
        return 4
    if ss["cohort"] is not None:
        return 3  # coorte pronta → seleção de features
    if ss["raw_data"] or ss["outcome_key"]:
        return 2  # dados baixados ou desfecho selecionado → ainda no passo Dados/Coorte
    return 1


def render_topbar() -> None:
    st.markdown(
        '<div class="ds-topbar">'
        '<a class="ds-topbar-logo" href="/" target="_self">'
        '<span class="ms" style="font-size:1.2rem;color:#111827">local_hospital</span>'
        'DataSUS AI'
        '<span class="ds-topbar-badge">PREDICTION</span>'
        '</a>'
        '<a class="ds-topbar-right" href="/" target="_self">Modelagem preditiva em saúde pública</a>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_step_bar(step: int) -> None:
    labels = ["Desfecho", "Dados", "Features", "Tratamento", "Modelo", "Treinamento", "Resultados", "Calibração", "Benchmark", "Deploy"]
    optionals = {8, 9, 10}
    parts = []
    for i, lbl in enumerate(labels):
        n = i + 1
        optional = n in optionals
        if n < step:
            cls, dot = "ds-step ds-step-done", "✓"
        elif n == step:
            cls, dot = "ds-step ds-step-active", str(n)
        else:
            cls = "ds-step ds-step-optional" if optional else "ds-step ds-step-locked"
            dot = str(n)
        suffix = " *" if optional else ""
        parts.append(f'<span class="{cls}">{dot}. {lbl}{suffix}</span>')
        if i < len(labels) - 1:
            parts.append('<span class="ds-step-arrow">›</span>')
    st.markdown(
        '<div class="ds-stepbar">' + "".join(parts) + "</div>",
        unsafe_allow_html=True,
    )


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
            st.rerun()


def step_title(n: int, title: str, caption: str = "") -> None:
    st.markdown(
        f'<p class="ds-section-title">Passo {n} — {title}</p>'
        + (f'<p class="ds-section-caption">{caption}</p>' if caption else ""),
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            '<div class="ds-sidebar-note">'
            '<div class="ds-sidebar-note-box">'
            '<strong style="color:#374151">Nota:</strong> Esta análise é independente e baseada em dados '
            'públicos da plataforma DATASUS. Não representa posicionamento oficial do Ministério da Saúde.'
            '</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<p class="sb-title">Pipeline</p>', unsafe_allow_html=True)

        # Step 1: Desfecho
        if ss.get("outcome_key"):
            o = OUTCOMES[ss["outcome_key"]]
            src_txt = ", ".join(o.data_sources)
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">1 · Desfecho</div>'
                f'<div class="sb-step-value">{o.name}<br>'
                f'<span style="font-size:.7rem;color:var(--muted)">{src_txt}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Editar", key="sb_chg_outcome"):
                for k in ["outcome_key", "raw_data", "cohort", "model_config",
                          "model_results", "calib_results", "comparison_results", "manual_needed"]:
                    ss[k] = _defaults[k]
                st.rerun()

        # Step 2: Dados
        if ss.get("raw_data"):
            lines = "<br>".join(f"{src}: {len(df):,}" for src, df in ss["raw_data"].items())
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">2 · Dados</div>'
                f'<div class="sb-step-value">{lines}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Editar", key="sb_chg_data"):
                for k in ["raw_data", "cohort", "model_config", "model_results",
                          "calib_results", "comparison_results", "manual_needed"]:
                    ss[k] = _defaults[k]
                st.rerun()

        # Step 3: Coorte
        if ss.get("cohort") is not None:
            n_ = len(ss["cohort"])
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">3 · Coorte</div>'
                f'<div class="sb-step-value">{n_:,} registros</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Editar", key="sb_chg_cohort"):
                ss["cohort"] = None
                for k in ["feature_config", "model_config", "model_results", "calib_results", "comparison_results"]:
                    ss[k] = _defaults[k]
                st.rerun()

        # Step 4: Features
        if ss.get("feature_config"):
            fc_ = ss["feature_config"]
            n_f = len(fc_["selected_features"])
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">4 · Features</div>'
                f'<div class="sb-step-value">{n_f} variáveis</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Editar", key="sb_chg_features"):
                for k in ["feature_config", "treatment_config", "model_config",
                          "model_results", "calib_results", "comparison_results"]:
                    ss[k] = _defaults[k]
                st.rerun()

        # Step 5: Tratamento
        if ss.get("treatment_config"):
            tc_ = ss["treatment_config"]
            _num_lbl = {"none": "Sem escala", "standard": "Z-score", "minmax": "Min-Max"}.get(
                tc_.get("num_default", "none"), "—")
            _cat_lbl = {"ohe": "One-Hot", "ordinal": "Ordinal", "target": "Target", "drop": "Remover"}.get(
                tc_.get("cat_default", "ohe"), "—")
            _n_ov = len(tc_.get("overrides", {}))
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">5 · Tratamento</div>'
                f'<div class="sb-step-value">'
                f'Num: {_num_lbl} · Cat: {_cat_lbl}'
                + (f'<br><span style="font-size:.7rem;color:var(--muted)">{_n_ov} ajuste(s) manual(is)</span>' if _n_ov else "")
                + f'</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("Editar", key="sb_chg_treatment"):
                for k in ["treatment_config", "model_config", "model_results",
                          "calib_results", "comparison_results"]:
                    ss[k] = _defaults[k]
                st.rerun()

        # Step 6: Modelo configurado
        if ss.get("model_config"):
            cfg_ = ss["model_config"]
            if cfg_["val_strategy"] == "Validação cruzada (k-fold)":
                _vs = f"{cfg_['n_folds']}-fold CV"
            elif cfg_["val_strategy"] == "Validação Temporal":
                _vs = f"Temporal · {cfg_.get('temporal_cutoff', '')[:7]}"
            else:
                _vs = f"Holdout {cfg_['holdout_size']:.0%}"
            _fc_ = ss.get("feature_config") or {}
            _nf = len(_fc_.get("selected_features", []))
            _albl = " · ".join(cfg_.get("algo_labels", [cfg_["algo_label"]]))
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">6 · Modelo</div>'
                f'<div class="sb-step-value">{_albl}<br>'
                f'<span style="font-size:.7rem;color:var(--muted)">{_vs} · {_nf} features</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Editar", key="sb_chg_model_config"):
                for k in ["model_config", "model_results", "calib_results", "comparison_results"]:
                    ss[k] = _defaults[k]
                st.rerun()

        # Step 5: Treinamento
        if ss.get("model_results"):
            r_ = ss["model_results"]
            m_ = r_["mean_metrics"]
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">7 · Treinamento</div>'
                f'<div class="sb-step-value">'
                f'AUC {m_["roc_auc"]:.3f} · F1 {m_["f1"]:.3f}<br>'
                f'<span style="font-size:.7rem;color:var(--muted)">PR-AUC {m_["pr_auc"]:.3f}</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Retreinar", key="sb_chg_model"):
                for k in ["model_results", "calib_results", "comparison_results"]:
                    ss[k] = _defaults[k]
                st.rerun()


# ── Topbar + wrapper ──────────────────────────────────────────────────────────
render_topbar()
render_sidebar()
st.markdown('<div class="ds-page">', unsafe_allow_html=True)
render_step_bar(current_step())


# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 1 — DESFECHO
# ═════════════════════════════════════════════════════════════════════════════
if not ss["outcome_key"]:
    step_title(1, "Selecionar Desfecho",
               "Escolha o desfecho clínico que deseja predizer. Organizado por área temática.")
    for group_name, keys in OUTCOME_GROUPS.items():
        st.markdown(f'<p class="ds-group-label">{group_name}</p>', unsafe_allow_html=True)
        # single-source first, multi-source last
        _sorted_keys = sorted(
            [k for k in keys if OUTCOMES.get(k)],
            key=lambda k: len(OUTCOMES[k].data_sources),
        )
        N_COLS = 3
        for row_start in range(0, len(_sorted_keys), N_COLS):
            row_keys = _sorted_keys[row_start : row_start + N_COLS]
            cols = st.columns(N_COLS)
            for col_idx, key in enumerate(row_keys):
                outcome = OUTCOMES[key]
                with cols[col_idx]:
                    is_sel = ss["outcome_key"] == key
                    cls = "ds-card selected" if is_sel else "ds-card"
                    st.markdown(
                        f'<div class="{cls}">'
                        f'<div class="ds-card-title">{outcome.name}</div>'
                        f'<div class="ds-card-desc">{outcome.description[:108]}…</div>'
                        f'<div class="ds-card-meta">{", ".join(outcome.data_sources)}'
                        f' &nbsp;·&nbsp; ~{outcome.estimated_download_min} min</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        "Selecionado" if is_sel else "Selecionar",
                        key=f"sel_{key}",
                        type="primary" if is_sel else "secondary",
                    ):
                        for k in ["raw_data", "cohort", "model_config", "model_results", "manual_needed"]:
                            ss[k] = _defaults[k]
                        ss["outcome_key"] = key
                        st.rerun()
    st.stop()

outcome = OUTCOMES[ss["outcome_key"]]

# ── Lazy: módulos de dados e visualização (step 2+) ──────────────────────────
pd = _pd()
px = _px()
STATES, ManualUploadRequired, fetch, load_from_csv = _dl()

# ─── Steps 2-3: apenas quando coorte ainda não foi construída ────────────────
if ss["cohort"] is None:
    # ═════════════════════════════════════════════════════════════════════════
    # ETAPA 2 — DADOS
    # ═════════════════════════════════════════════════════════════════════════
    if not ss["raw_data"]:
        step_title(2, "Dados",
                   f"Fontes necessárias para este desfecho: {', '.join(outcome.data_sources)}")

        # ── Linha 1: Estado + Ano + Botão ─────────────────────────────────────────
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            ss["sel_states"] = st.multiselect("Estados (UF)", STATES, default=ss["sel_states"])
        with c2:
            ss["sel_years"] = st.multiselect("Anos", list(range(2018, 2025)), default=ss["sel_years"])

        if not ss["sel_states"] or not ss["sel_years"]:
            st.info("Selecione pelo menos um estado e um ano para continuar.")
            st.stop()

        with c3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            _download_clicked = st.button("Baixar", type="primary")

        # ── Linha 2: Limite de registros ───────────────────────────────────────────
        st.markdown("<div style='margin-top:.75rem'></div>", unsafe_allow_html=True)
        with st.expander("Limite de registros por download", expanded=False):
            sa1, sa2 = st.columns(2)
            with sa1:
                ss["sample_n"] = st.number_input(
                    "Máximo de registros",
                    min_value=1_000,
                    max_value=500_000,
                    value=ss["sample_n"],
                    step=5_000,
                    help="Limita o download para evitar falta de memória. Padrão: 1.000. Use 500.000 para dados completos.",
                )
            with sa2:
                ss["sample_seed"] = st.number_input(
                    "Seed (reprodutibilidade)",
                    min_value=0, max_value=99_999,
                    value=ss["sample_seed"], step=1,
                    help="Seed aleatória para garantir resultados reproduzíveis.",
                )
            st.caption(
                f"Serão baixados até **{ss['sample_n']:,}** registros com seed **{ss['sample_seed']}**. "
                "O limite é aplicado durante a leitura dos arquivos para economizar memória."
            )

        if _download_clicked:
            raw_data: dict = {}
            manual_needed: list = []
            _sample_n    = int(ss["sample_n"])
            _sample_seed = int(ss["sample_seed"])
            # Quota por arquivo para não estourar memória antes do concat
            _quota_per_file = max(1_000, _sample_n // max(len(ss["sel_states"]) * len(ss["sel_years"]), 1))

            for source in outcome.data_sources:
                prog = st.progress(0.0, text=f"Baixando {source}…")
                try:
                    dfs = []
                    for state in ss["sel_states"]:
                        for year in ss["sel_years"]:
                            # max_rows limita leitura dentro do _dbc_to_df (evita OOM)
                            part = fetch(
                                source, state, year,
                                progress_callback=lambda p, m, _p=prog: _p.progress(min(p, 1.0), text=m),
                                max_rows=_quota_per_file,
                            )
                            dfs.append(part)

                    df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

                    # ── Garante o total exato após concat ──────────────────────────
                    if len(df) > _sample_n:
                        df = df.sample(n=_sample_n, random_state=_sample_seed).reset_index(drop=True)
                        prog.progress(1.0, text=f"{source}: {len(df):,} registros (limitado a {_sample_n:,})")
                    else:
                        prog.progress(1.0, text=f"{source}: {len(df):,} registros")

                    raw_data[source] = df
                except ManualUploadRequired as e:
                    prog.empty()
                    manual_needed.append((source, str(e)))
                except Exception as e:
                    prog.empty()
                    st.error(f"Erro ao baixar {source}: {e}")

            ss["raw_data"] = raw_data
            ss["cohort"] = None
            ss["model_config"] = None
            ss["model_results"] = None
            ss["manual_needed"] = manual_needed
            if raw_data and not manual_needed:
                st.rerun()

        if ss["manual_needed"]:
            st.warning("Upload manual necessário para alguns arquivos.")
            raw_data = ss.get("raw_data", {})
            for source, msg in ss["manual_needed"]:
                with st.expander(f"Upload: {source}", expanded=True):
                    st.caption(msg)
                    uploaded = st.file_uploader(
                        f"CSV do {source}", type=["csv", "txt"], key=f"up_{source}"
                    )
                    if uploaded:
                        try:
                            s0 = ss["sel_states"][0] if len(ss["sel_states"]) == 1 else "BR"
                            y0 = ss["sel_years"][0] if len(ss["sel_years"]) == 1 else 0
                            df = load_from_csv(uploaded.read(), source, s0, y0)
                            raw_data[source] = df
                            ss["raw_data"] = raw_data
                            ss["cohort"] = None
                            st.success(f"{source}: {len(df):,} registros.")
                        except Exception as e:
                            st.error(f"Erro: {e}")
            if set(outcome.data_sources) <= set(raw_data.keys()):
                ss["manual_needed"] = []
                st.rerun()

        st.stop()

    # ── Lazy: CohortBuilder ───────────────────────────────────────────────────
    CohortBuilder = _cohort()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("**Revisar e Construir Coorte**")
    st.caption("Revise os dados baixados e confirme para construir a coorte de modelagem.")

    # ── Preview dos dados brutos ──────────────────────────────────────────────
    _sources = list(ss["raw_data"].keys())
    _tabs = st.tabs(_sources) if len(_sources) > 1 else [st.container()]

    for _tab, _src in zip(_tabs, _sources):
        with _tab:
            _df = ss["raw_data"][_src]
            _n, _k = _df.shape

            # Linha de resumo
            _c1, _c2, _c3 = st.columns(3)
            _c1.metric("Registros", f"{_n:,}")
            _c2.metric("Colunas", str(_k))
            _miss_total = int(_df.isna().sum().sum())
            _miss_pct = _miss_total / max(_n * _k, 1)
            _c3.metric("Completude geral", f"{1 - _miss_pct:.1%}")

            # Sumário estatístico
            with st.expander("Sumário estatístico", expanded=False):
                import plotly.express as _px_s
                import math as _math

                _num = _df.select_dtypes(include="number")
                _cat = _df.select_dtypes(exclude="number")

                if not _num.empty:
                    st.markdown("**Variáveis numéricas**")
                    st.dataframe(_num.describe().T.round(2), use_container_width=True)

                if not _cat.empty:
                    st.markdown("**Distribuição de variáveis categóricas**")
                    _cat_cols = _cat.columns.tolist()
                    _ncols = 2
                    _nrows = _math.ceil(len(_cat_cols) / _ncols)
                    for _row_i in range(_nrows):
                        _grid = st.columns(_ncols)
                        for _col_i in range(_ncols):
                            _ci = _row_i * _ncols + _col_i
                            if _ci >= len(_cat_cols):
                                break
                            _col_name = _cat_cols[_ci]
                            _vc = (
                                _df[_col_name]
                                .astype(str)
                                .value_counts()
                                .reset_index()
                            )
                            _vc.columns = ["Categoria", "Contagem"]
                            _fig_cat = _px_s.bar(
                                _vc,
                                x="Categoria",
                                y="Contagem",
                                title=_col_name,
                                color="Contagem",
                                color_continuous_scale="Blues",
                            )
                            _fig_cat.update_layout(
                                coloraxis_showscale=False,
                                margin=dict(l=0, r=0, t=40, b=0),
                                plot_bgcolor="white",
                                paper_bgcolor="white",
                                showlegend=False,
                                height=280,
                                font=dict(size=11),
                            )
                            _fig_cat.update_xaxes(tickangle=-35)
                            _grid[_col_i].plotly_chart(_fig_cat, use_container_width=True)

                if _num.empty and _cat.empty:
                    st.caption("Nenhuma coluna encontrada.")

            # Completude por coluna
            with st.expander("Completude por coluna", expanded=False):
                import plotly.express as _px_c
                _miss_s = _df.isna().mean().sort_values(ascending=False)
                _miss_df = pd.DataFrame({
                    "Coluna": _miss_s.index,
                    "Preenchido (%)": ((1 - _miss_s.values) * 100).round(1),
                    "Missing (%)": (_miss_s.values * 100).round(1),
                }).reset_index(drop=True)
                _high = _miss_df["Missing (%)"] > 50

                # gráfico de barras horizontais empilhadas
                _fig_comp = _px_c.bar(
                    _miss_df,
                    y="Coluna",
                    x=["Preenchido (%)", "Missing (%)"],
                    orientation="h",
                    color_discrete_map={"Preenchido (%)": "#22c55e", "Missing (%)": "#f97316"},
                    labels={"value": "%", "variable": ""},
                    height=max(300, _k * 22),
                )
                _fig_comp.update_layout(
                    barmode="stack",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=0, r=0, t=30, b=0),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    xaxis=dict(range=[0, 100], ticksuffix="%"),
                    yaxis=dict(autorange="reversed"),
                    font=dict(size=12),
                )
                st.plotly_chart(_fig_comp, use_container_width=True)
                if _high.any():
                    st.caption(
                        f"⚠ {int(_high.sum())} coluna(s) com mais de 50% de missing — "
                        "serão imputadas pela mediana no pipeline."
                    )

            # Amostra
            with st.expander("Amostra dos dados (10 linhas)"):
                st.dataframe(_df.head(10), use_container_width=True, hide_index=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Construir Coorte", type="primary"):
        with st.spinner("Construindo coorte…"):
            try:
                builder = CohortBuilder(outcome)
                ss["cohort"] = builder.build(ss["raw_data"])
                ss["model_config"] = None
                ss["model_results"] = None
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao construir coorte: {e}")
                st.exception(e)
    st.stop()

# ─── COHORT BUILT: Steps 4-9 ────────────────────────────────────────────────

# ── Lazy: CohortBuilder e pipeline ML ────────────────────────────────────────
CohortBuilder = _cohort()
ALGORITHMS, train_cv, optimize_hyperparams, calibrate_model, build_pipeline, random_search, grid_search = _pipeline()

cohort = ss["cohort"]
builder = CohortBuilder(outcome)
X, y = builder.get_Xy(cohort)

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 4 — FEATURES
# ═════════════════════════════════════════════════════════════════════════════
if not ss.get("feature_config"):
    from core.features.data_dict import get_info as _feat_info

    step_title(3, "Selecionar Features",
               "Escolha as variáveis a incluir no modelo e consulte o dicionário de dados.")

    bal = builder.class_balance(cohort)
    total_n = bal["total"]
    all_features = X.columns.tolist()
    st.info(
        f"**{total_n:,}** registros · prevalência **{bal['prevalence']:.1%}** · "
        f"**{len(all_features)}** features disponíveis"
    )

    selected_features = st.multiselect(
        "Features para o modelo",
        all_features,
        default=all_features,
        help="Selecione as variáveis a usar no modelo. Remova features irrelevantes ou com alto missing.",
    )
    if not selected_features:
        st.warning("Selecione pelo menos uma feature.")
        st.stop()

    # ── Dicionário de dados ────────────────────────────────────────────────
    with st.expander(f"Dicionário de dados — {len(selected_features)} features selecionadas", expanded=False):
        _type_colors = {
            "Numérica": "#111827",
            "Categórica": "#374151",
            "Ordinal": "#374151",
            "Derivada": "#6b7280",
        }
        for _feat in selected_features:
            _info = _feat_info(_feat)
            _col_a, _col_b = st.columns([3, 1])
            with _col_a:
                if _info:
                    st.markdown(
                        f"**{_feat}** &nbsp;—&nbsp; {_info['label']}  \n"
                        f"<span style='font-size:.8rem;color:#4b5563'>{_info['desc']}</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"**{_feat}**  \n"
                        f"<span style='font-size:.8rem;color:#9ca3af'>Sem descrição disponível.</span>",
                        unsafe_allow_html=True,
                    )
            with _col_b:
                _type_lbl = _info.get("type", "") if _info else ""
                if _type_lbl:
                    _type_color = _type_colors.get(_type_lbl, "#6b7280")
                    st.markdown(
                        f"<div style='text-align:right;margin-top:2px'>"
                        f"<span style='font-size:.68rem;font-weight:600;color:{_type_color}'>"
                        f"{_type_lbl}</span></div>",
                        unsafe_allow_html=True,
                    )
            st.markdown("<hr style='border:none;border-top:1px solid #f3f4f6;margin:6px 0'>",
                        unsafe_allow_html=True)

    if st.button("Confirmar Features", type="primary"):
        ss["feature_config"] = {"selected_features": selected_features}
        ss["treatment_config"] = None
        ss["model_config"] = None
        ss["model_results"] = None
        ss["calib_results"] = None
        ss["comparison_results"] = []
        st.rerun()
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 5 — TRATAMENTO DE VARIÁVEIS
# ═════════════════════════════════════════════════════════════════════════════
if not ss.get("treatment_config"):
    step_title(4, "Tratamento de Variáveis",
               "Classifique o tipo de cada variável e configure o tratamento.")

    _sel_feats = ss["feature_config"]["selected_features"]
    X_sel = X[_sel_feats]
    _num_cols_orig = X_sel.select_dtypes(include="number").columns.tolist()
    _cat_cols_orig = X_sel.select_dtypes(include=["object", "category"]).columns.tolist()
    _low_card = [c for c in _num_cols_orig if 1 < X_sel[c].nunique() <= 10]

    # ── Passo 1: Classificar tipo por variável ────────────────────────────────
    st.markdown("**Passo 1 — Classificar tipo de cada variável**")
    if _low_card:
        st.caption(
            f"Variáveis com baixa cardinalidade: **{', '.join(_low_card)}** — "
            "podem ser tratadas como categóricas."
        )

    from core.features.data_dict import get_info as _dd_info
    _type_opts = ["Numérica", "Categórica", "Remover"]
    _type_result: dict = {}

    def _infer_type(col: str) -> str:
        """Infer variable type from data dictionary; fall back to pandas dtype."""
        info = _dd_info(col)
        if info:
            dd_type = info.get("type", "")
            if dd_type == "Numérica":
                return "Numérica"
            if dd_type in ("Categórica", "Ordinal"):
                return "Categórica"
        # fallback: pandas dtype
        return "Numérica" if col in _num_cols_orig else "Categórica"

    with st.expander(f"Classificação por variável — {len(_sel_feats)} features", expanded=False):
        _th1, _th2, _th3 = st.columns([3, 2, 1])
        _th1.markdown("<div style='font-size:.72rem;font-weight:600;color:#6b7280'>VARIÁVEL</div>", unsafe_allow_html=True)
        _th2.markdown("<div style='font-size:.72rem;font-weight:600;color:#6b7280'>TIPO</div>", unsafe_allow_html=True)
        _th3.markdown("<div style='font-size:.72rem;font-weight:600;color:#6b7280'>INFO</div>", unsafe_allow_html=True)
        for _col in _sel_feats:
            _nuniq = X_sel[_col].nunique()
            _inferred = _infer_type(_col)
            _vc1, _vc2, _vc3 = st.columns([3, 2, 1])
            with _vc1:
                st.markdown(
                    f"<div style='padding:5px 0;font-size:.82rem'><b>{_col}</b> "
                    f"<span style='color:#9ca3af;font-size:.72rem'>({_nuniq} únicos)</span></div>",
                    unsafe_allow_html=True,
                )
            with _vc2:
                _type_result[_col] = st.selectbox(
                    _col, _type_opts,
                    index=_type_opts.index(_inferred),
                    key=f"type_{_col}",
                    label_visibility="collapsed",
                )
            with _vc3:
                if _col in _low_card:
                    st.markdown(
                        "<div style='padding:5px 0;font-size:.68rem;color:#d97706'>baixa card.</div>",
                        unsafe_allow_html=True,
                    )

    # Listas finais baseadas na classificação do usuário
    _num_cols = [c for c, t in _type_result.items() if t == "Numérica"]
    _cat_cols = [c for c, t in _type_result.items() if t == "Categórica"]

    _ti1, _ti2, _ti3 = st.columns(3)
    _ti1.metric("Numéricas", str(len(_num_cols)))
    _ti2.metric("Categóricas", str(len(_cat_cols)))
    _ti3.metric("Removidas", str(len(_sel_feats) - len(_num_cols) - len(_cat_cols)))

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Passo 2: Configurar tratamento ────────────────────────────────────────
    st.markdown("**Passo 2 — Configurar tratamento**")

    _all_num_opts = ["none", "standard", "minmax", "drop"]
    _all_cat_opts = ["ohe", "ordinal", "target", "drop"]
    _num_lbl_map = {"none": "Nenhuma", "standard": "Z-score", "minmax": "Min-Max", "drop": "Remover"}
    _cat_lbl_map = {"ohe": "One-Hot", "ordinal": "Ordinal", "target": "Target", "drop": "Remover"}

    _num_map = {
        "Nenhuma (recomendado para árvores)": "none",
        "Padronização (z-score)": "standard",
        "Normalização (min-max)": "minmax",
    }
    _cat_map = {
        "One-Hot Encoding": "ohe",
        "Ordinal Encoding": "ordinal",
        "Target Encoding": "target",
        "Remover": "drop",
    }

    _overrides: dict = {}

    # ── Row 1: radio buttons (altura independente por coluna) ──────────────────
    _r1, _r2 = st.columns(2)
    with _r1:
        st.markdown("**Variáveis Numéricas**")
        _num_opt = st.radio(
            "Escala padrão",
            list(_num_map.keys()),
            label_visibility="collapsed",
        )
    with _r2:
        st.markdown("**Variáveis Categóricas**")
        _cat_opt = st.radio(
            "Codificação padrão",
            list(_cat_map.keys()),
            label_visibility="collapsed",
            help=(
                "**One-Hot**: cria coluna binária por categoria. "
                "**Ordinal**: converte em inteiro (variáveis com ordem natural). "
                "**Target**: média do target por categoria (alta cardinalidade). "
                "**Remover**: exclui a variável do modelo."
            ),
        )

    # ── Ajustes por variável ──────────────────────────────────────────────────
    _num_treat_opts = ["none", "standard", "minmax", "drop"]
    _cat_treat_opts = ["ohe", "ordinal", "target", "drop"]
    _num_lbl = {"none": "Nenhuma", "standard": "Z-score", "minmax": "Min-Max", "drop": "Remover"}
    _cat_lbl = {"ohe": "One-Hot", "ordinal": "Ordinal", "target": "Target", "drop": "Remover"}

    # track effective type per column (after user override)
    _eff_type: dict = {}      # col -> "num" | "cat"
    _treat_override: dict = {}  # col -> treatment key

    with st.expander(f"Ajustes por variável — {len(_sel_feats)} features", expanded=False):
        # Header
        _hc1, _hc2, _hc3 = st.columns([3, 2, 2])
        for _hcol, _htxt in zip([_hc1, _hc2, _hc3],
                                 ["Variável", "Tipo", "Tratamento"]):
            _hcol.markdown(
                f"<div style='font-size:.68rem;font-weight:700;color:#9ca3af;"
                f"text-transform:uppercase;letter-spacing:.08em;padding-bottom:4px'>"
                f"{_htxt}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("<hr style='border:none;border-top:1px solid #f3f4f6;margin:0 0 4px'>",
                    unsafe_allow_html=True)

        for _col in _sel_feats:
            _detected = "cat" if _col in _cat_cols else "num"
            _nuniq = X_sel[_col].nunique()
            _is_low = _col in _low_card

            _vc1, _vc2, _vc3 = st.columns([3, 2, 2])

            with _vc1:
                _badge = (" <span style='font-size:.65rem;color:#d97706;"
                          "font-weight:600'>baixa card.</span>") if _is_low else ""
                st.markdown(
                    f"<div style='padding:5px 0;font-size:.82rem'>"
                    f"<b>{_col}</b>"
                    f"<span style='color:#9ca3af;font-size:.72rem'> ({_nuniq} únicos)</span>"
                    f"{_badge}</div>",
                    unsafe_allow_html=True,
                )

            with _vc2:
                _type_sel = st.selectbox(
                    f"type_{_col}",
                    ["Numérica", "Categórica"],
                    index=0 if _detected == "num" else 1,
                    key=f"tp_{_col}",
                    label_visibility="collapsed",
                )
                _eff = "num" if _type_sel == "Numérica" else "cat"
                _eff_type[_col] = _eff

            with _vc3:
                if _eff == "num":
                    _opts = _num_treat_opts
                    _lbl_map = _num_lbl
                    _def_idx = _opts.index(_num_default_key)
                else:
                    _opts = _cat_treat_opts
                    _lbl_map = _cat_lbl
                    _def_idx = _opts.index(_cat_default_key)

                _treat_sel = st.selectbox(
                    f"treat_{_col}",
                    _opts,
                    format_func=lambda x, m=_lbl_map: m[x],
                    index=_def_idx,
                    key=f"tr_{_col}",
                    label_visibility="collapsed",
                )
                _expected = _num_default_key if _eff == "num" else _cat_default_key
                if _treat_sel != _expected:
                    _treat_override[_col] = _treat_sel

            st.markdown("<hr style='border:none;border-top:1px solid #f9fafb;margin:0'>",
                        unsafe_allow_html=True)

    # Compute effective column lists after type overrides
    _eff_num_cols = [c for c in _sel_feats if _eff_type.get(c, "num" if c in _num_cols else "cat") == "num"]
    _eff_cat_cols = [c for c in _sel_feats if _eff_type.get(c, "num" if c in _num_cols else "cat") == "cat"]

    if st.button("Confirmar Tratamento", type="primary"):
        ss["treatment_config"] = {
            "num_cols": _eff_num_cols,
            "cat_cols": _eff_cat_cols,
            "num_default": _num_default_key,
            "cat_default": _cat_default_key,
            "overrides": _treat_override,
        }
        ss["model_config"] = None
        ss["model_results"] = None
        ss["calib_results"] = None
        ss["comparison_results"] = []
        st.rerun()
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 6 — CONFIGURAR MODELO
# ═════════════════════════════════════════════════════════════════════════════
if not ss.get("model_config"):
    step_title(5, "Configurar Modelo",
               "Configure os algoritmos, validação e hiperparâmetros.")
    bal = builder.class_balance(cohort)
    total_n = bal["total"]
    st.info(
        f"**{total_n:,}** registros · prevalência **{bal['prevalence']:.1%}** · "
        f"**{len(X.columns)}** features disponíveis"
    )

    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

    # ── Algoritmos ────────────────────────────────────────────────────────────
    algo_labels = st.multiselect(
        "Algoritmos",
        list(ALGORITHMS.keys()),
        default=["LightGBM"],
        help="Selecione um ou mais algoritmos para treinar e comparar.",
    )
    if not algo_labels:
        st.warning("Selecione pelo menos um algoritmo.")
        st.stop()
    algos = [ALGORITHMS[l] for l in algo_labels]

    # Aviso TabPFN sobre disponibilidade e limite de amostras
    if "tabpfn" in algos:
        from core.models.pipeline import TABPFN_MAX_TRAIN_SAMPLES, TABPFN_WARN_TRAIN_SAMPLES, TABPFN_AVAILABLE
        if not TABPFN_AVAILABLE:
            st.error(
                "**TabPFN não está instalado** neste ambiente. "
                "Instale com `pip install tabpfn` (requer torch ~1 GB) ou remova TabPFN da seleção."
            )

        _n_total = builder.class_balance(cohort)["total"]
        if _n_total > TABPFN_MAX_TRAIN_SAMPLES:
            st.error(
                f"**TabPFN não suporta mais de {TABPFN_MAX_TRAIN_SAMPLES:,} amostras** "
                f"(coorte atual: {_n_total:,}). "
                "Reduza o tamanho da amostra no Passo 2 ou remova TabPFN da seleção."
            )
        elif _n_total > TABPFN_WARN_TRAIN_SAMPLES:
            st.warning(
                f"**TabPFN:** desempenho ótimo com até {TABPFN_WARN_TRAIN_SAMPLES:,} amostras "
                f"(coorte atual: {_n_total:,}). Acima disso o modelo pode ser mais lento e menos preciso."
            )

    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

    # ── 3 blocos de configuração ──────────────────────────────────────────────
    b1, b2, b3 = st.columns(3)

    with b1:
        st.markdown("**Estratégia de Validação**")
        val_strategy = st.radio(
            "Validação",
            ["Validação cruzada (k-fold)", "Holdout (train/test)", "Validação Temporal"],
            label_visibility="collapsed",
        )
        if val_strategy == "Validação cruzada (k-fold)":
            n_folds = st.slider("Folds", 3, 10, 5)
            holdout_size = 0.20
            temporal_date_col = None
            temporal_cutoff = None
        elif val_strategy == "Holdout (train/test)":
            holdout_size = st.select_slider(
                "Proporção de teste",
                options=[0.10, 0.15, 0.20, 0.25, 0.30],
                value=0.20,
                format_func=lambda x: f"{x:.0%}",
            )
            n_folds = 1
            temporal_date_col = None
            temporal_cutoff = None
        else:
            # Validação Temporal
            import pandas as _pd_tmp
            _date_candidates = [
                c for c in cohort.columns
                if _pd_tmp.api.types.is_datetime64_any_dtype(cohort[c])
                or any(kw in c.upper() for kw in ["DT_", "DTNASC", "DATA", "DATE"])
            ]
            temporal_date_col = st.selectbox(
                "Coluna de data",
                options=_date_candidates if _date_candidates else cohort.columns.tolist(),
                help="Coluna usada para ordenar os registros no tempo.",
            )
            # Calcula min/max da coluna selecionada
            try:
                _ts = _pd_tmp.to_datetime(cohort[temporal_date_col], errors="coerce").dropna()
                _dt_min = _ts.min().date()
                _dt_max = _ts.max().date()
                _dt_default = _ts.quantile(0.80).date() if len(_ts) else _dt_min
            except Exception:
                import datetime
                _dt_min = datetime.date(2018, 1, 1)
                _dt_max = datetime.date(2024, 12, 31)
                _dt_default = datetime.date(2023, 1, 1)
            temporal_cutoff = st.date_input(
                "Data de corte (treino ← antes · teste → depois)",
                value=_dt_default,
                min_value=_dt_min,
                max_value=_dt_max,
                help="Registros anteriores à data de corte são usados no treino; posteriores, no teste.",
            )
            # Info sobre tamanho do split
            try:
                _ts_full = _pd_tmp.to_datetime(cohort[temporal_date_col], errors="coerce")
                _n_train = int((_ts_full < _pd_tmp.Timestamp(temporal_cutoff)).sum())
                _n_test  = int((_ts_full >= _pd_tmp.Timestamp(temporal_cutoff)).sum())
                st.caption(f"Treino: {_n_train:,} · Teste: {_n_test:,}")
            except Exception:
                pass
            n_folds = 1
            holdout_size = 0.20

    with b2:
        st.markdown("**Balanceamento de Classes**")
        balancing = st.radio(
            "Balanceamento",
            ["Nenhum", "Class Weight", "SMOTE (oversample)", "SMOTE + Undersampling"],
            label_visibility="collapsed",
            help=(
                "**Nenhum**: sem ajuste. "
                "**Class Weight**: penaliza erros na classe minoritária via class_weight='balanced'. "
                "**SMOTE (oversample)**: gera amostras sintéticas da classe minoritária. "
                "**SMOTE + Undersampling**: combina SMOTE com remoção de exemplos (SMOTETomek)."
            ),
        )
        _bal_map = {
            "Nenhum": "none",
            "Class Weight": "class_weight",
            "SMOTE (oversample)": "smote_over",
            "SMOTE + Undersampling": "smote_under",
        }
        balancing_key = _bal_map[balancing]

    with b3:
        st.markdown("**Estratégia de Hiperparâmetros**")
        hpo_mode = st.radio(
            "HPO",
            ["Optuna (automático)", "Random Search", "Grid Search", "Manual"],
            index=0,
            label_visibility="collapsed",
            help=(
                "**Optuna**: otimização bayesiana automática (melhor custo-benefício). "
                "**Random Search**: amostragem aleatória do espaço (rápido). "
                "**Grid Search**: busca exaustiva em grade pré-definida. "
                "**Manual**: defina os parâmetros abaixo."
            ),
        )
        if hpo_mode == "Random Search":
            n_iter = st.slider("Iterações (n_iter)", 5, 100, 10, 5)
            n_trials = 5
        elif hpo_mode == "Optuna (automático)":
            n_trials = st.slider("Tentativas (trials)", 5, 200, 5, 5)
            n_iter = 10
        else:
            n_iter = 10
            n_trials = 5

    # ── Hiperparâmetros manuais (só quando Manual selecionado) ────────────────
    params_per_algo: dict = {a: {} for a in algos}
    if hpo_mode == "Manual":
        st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
        st.markdown("**Hiperparâmetros**")
        _pcols = st.columns(max(len(algos), 1))
        for _i, (_algo, _lbl) in enumerate(zip(algos, algo_labels)):
            with _pcols[_i]:
                if len(algos) > 1:
                    st.caption(f"**{_lbl}**")
                _p: dict = {}
                if _algo in ("lgbm", "xgb", "rf"):
                    _p["n_estimators"] = st.slider(
                        "n_estimators", 50, 1000, 300, 50, key=f"ne_{_algo}")
                if _algo in ("lgbm", "xgb"):
                    _p["learning_rate"] = st.select_slider(
                        "learning_rate",
                        [0.005, 0.01, 0.02, 0.05, 0.1, 0.2], value=0.05,
                        key=f"lr_{_algo}")
                if _algo in ("lgbm", "xgb", "rf"):
                    _p["max_depth"] = st.slider(
                        "max_depth (−1 = sem limite)", -1, 15, -1, key=f"md_{_algo}")
                if _algo == "catboost":
                    _p["iterations"] = st.slider(
                        "iterations", 50, 1000, 300, 50, key=f"it_{_algo}")
                    _p["learning_rate"] = st.select_slider(
                        "learning_rate",
                        [0.005, 0.01, 0.02, 0.05, 0.1, 0.2], value=0.05,
                        key=f"lr_{_algo}")
                    _p["depth"] = st.slider(
                        "depth", 2, 10, 6, key=f"dep_{_algo}")
                if _algo == "logreg":
                    _p["C"] = st.select_slider(
                        "C (regularização)",
                        [0.001, 0.01, 0.1, 1.0, 10.0], value=1.0,
                        key=f"c_{_algo}")
                params_per_algo[_algo] = _p

    if st.button("Confirmar Configuração", type="primary"):
        ss["model_config"] = {
            "algos": algos,
            "algo_labels": algo_labels,
            "algo": algos[0],
            "algo_label": algo_labels[0],
            "val_strategy": val_strategy,
            "n_folds": n_folds,
            "holdout_size": holdout_size,
            "temporal_date_col": temporal_date_col,
            "temporal_cutoff": str(temporal_cutoff) if temporal_cutoff else None,
            "balancing": balancing_key,
            "balancing_label": balancing,
            "hpo_mode": hpo_mode,
            "n_iter": n_iter,
            "n_trials": n_trials,
            "params": params_per_algo.get(algos[0], {}),
            "params_per_algo": params_per_algo,
        }
        ss["model_results"] = None
        ss["calib_results"] = None
        ss["comparison_results"] = []
        st.rerun()
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 7 — TREINAR
# ═════════════════════════════════════════════════════════════════════════════
cfg = ss["model_config"]
algos = cfg.get("algos", [cfg["algo"]])
algo_labels = cfg.get("algo_labels", [cfg["algo_label"]])
algo = algos[0]
algo_label = algo_labels[0]
_algos_label = " · ".join(algo_labels)
val_strategy = cfg["val_strategy"]
n_folds = cfg["n_folds"]
holdout_size = cfg["holdout_size"]
temporal_date_col = cfg.get("temporal_date_col")
temporal_cutoff = cfg.get("temporal_cutoff")
balancing = cfg.get("balancing", "none")
hpo_mode = cfg["hpo_mode"]
n_iter = cfg.get("n_iter", 30)
n_trials = cfg.get("n_trials", 5)
params_per_algo = cfg.get("params_per_algo", {algo: cfg.get("params", {})})
selected_features = ss["feature_config"]["selected_features"]
treatment = ss.get("treatment_config")

if not ss["model_results"]:
    step_title(6, "Treinar Modelo",
               "Execute o treinamento com a configuração selecionada.")
    bal = builder.class_balance(cohort)
    total_n = bal["total"]
    if val_strategy == "Validação cruzada (k-fold)":
        _val_tag_label = f"{n_folds}-fold CV"
    elif val_strategy == "Validação Temporal":
        _val_tag_label = f"Temporal · corte {temporal_cutoff}"
    else:
        _val_tag_label = f"Holdout {holdout_size:.0%}"
    st.info(
        f"**{_algos_label}** · {_val_tag_label} · **{len(selected_features)}** features · "
        f"**{total_n:,}** registros"
        + (f" · {cfg.get('balancing_label', '')}" if balancing != "none" else "")
        + (f" · Optuna {n_trials} trials" if hpo_mode == "Optuna (automático)" else "")
        + (f" · Random Search {n_iter} iter" if hpo_mode == "Random Search" else "")
        + (" · Grid Search" if hpo_mode == "Grid Search" else "")
    )

    X_model = X[selected_features]
    sample_n = total_n

    _LC_COLORS = [
        "#1a56db", "#e11d48", "#059669", "#7c3aed",
        "#d97706", "#0891b2", "#be185d", "#65a30d",
    ]

    def _lc_fig(lc_data: dict):
        """lc_data = {algo_label: {"sizes": [...], "val": [...], "train": [...]}}"""
        import plotly.graph_objects as _go

        # Calcula range dinâmico do eixo Y com padding
        all_vals = []
        for d in lc_data.values():
            all_vals.extend(d.get("val", []))
            all_vals.extend(d.get("train", []))
        if all_vals:
            _ymin = max(0.0, min(all_vals) - 0.05)
            _ymax = min(1.01, max(all_vals) + 0.03)
        else:
            _ymin, _ymax = 0.4, 1.0

        fig = _go.Figure()
        for i, (lbl, d) in enumerate(lc_data.items()):
            color = _LC_COLORS[i % len(_LC_COLORS)]
            if d["sizes"]:
                fig.add_trace(_go.Scatter(
                    x=d["sizes"], y=d["val"], mode="lines+markers",
                    name=f"{lbl} — Validação",
                    line=dict(color=color, width=2.5), marker=dict(size=8),
                ))
                if d["train"]:
                    fig.add_trace(_go.Scatter(
                        x=d["sizes"], y=d["train"], mode="lines+markers",
                        name=f"{lbl} — Treino",
                        line=dict(color=color, width=1.5, dash="dot"),
                        marker=dict(size=6, symbol="circle-open"),
                    ))
        fig.update_layout(
            title="Curva de Aprendizado — ROC-AUC por volume de dados",
            xaxis_title="Registros de treinamento",
            yaxis=dict(
                title="ROC-AUC",
                range=[_ymin, _ymax],
                gridcolor="rgba(0,0,0,0.07)",
                tickformat=".2f",
            ),
            xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.07)", zeroline=False),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=450,
            legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5),
            margin=dict(t=50, b=90, l=70, r=30),
            font=dict(size=13),
            hovermode="x unified",
        )
        return fig

    _lc_chart_ph = st.empty()
    _lc_status_ph = st.empty()
    _lc_chart_ph.plotly_chart(_lc_fig({}), use_container_width=True)

    _hpo_prefix = {
        "Optuna (automático)": "Optuna + ",
        "Random Search": "Random Search + ",
        "Grid Search": "Grid Search + ",
    }.get(hpo_mode, "")
    btn_label = f"{_hpo_prefix}Treinar {_algos_label} · {_val_tag_label}"

    if st.button(btn_label, type="primary"):
        try:
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import roc_auc_score as _roc_auc

            X_train = X_model
            y_train = y

            # ── Learning curve — uma curva por algoritmo, cores distintas ─────
            _fracs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
            _lc_data: dict = {lbl: {"sizes": [], "val": [], "train": []} for lbl in algo_labels}

            try:
                _X_lc, _X_hold, _y_lc, _y_hold = train_test_split(
                    X_train, y_train, test_size=0.2, stratify=y_train, random_state=42,
                )
            except Exception:
                _X_lc, _X_hold = X_train, X_train
                _y_lc, _y_hold = y_train, y_train

            for _lc_algo, _lc_lbl in zip(algos, algo_labels):
                for _frac in _fracs:
                    _n = max(30, int(len(_X_lc) * _frac))
                    try:
                        if _frac < 1.0:
                            _Xs, _, _ys, _ = train_test_split(
                                _X_lc, _y_lc, train_size=_n, stratify=_y_lc, random_state=42,
                            )
                        else:
                            _Xs, _ys = _X_lc, _y_lc
                        _qp = build_pipeline(_Xs, _lc_algo, {}, balancing="none", treatment=treatment)
                        _qp.fit(_Xs, _ys)
                        _tr_auc = float(_roc_auc(_ys, _qp.predict_proba(_Xs)[:, 1])) if _ys.sum() > 0 else 0.5
                        _vl_auc = float(_roc_auc(_y_hold, _qp.predict_proba(_X_hold)[:, 1])) if _y_hold.sum() > 0 else 0.5
                    except Exception:
                        _tr_auc = _vl_auc = 0.5
                    _lc_data[_lc_lbl]["sizes"].append(_n)
                    _lc_data[_lc_lbl]["train"].append(_tr_auc)
                    _lc_data[_lc_lbl]["val"].append(_vl_auc)
                    _lc_chart_ph.plotly_chart(_lc_fig(_lc_data), use_container_width=True)
                    _lc_status_ph.caption(
                        f"Curva de aprendizado ({_lc_lbl}) — {int(_frac*100)}% — Val AUC: {_vl_auc:.3f}"
                    )

            # ── Loop por algoritmo: HPO + treino ──────────────────────────────
            _hpo_folds = min(n_folds, 3) if val_strategy == "Validação cruzada (k-fold)" else 3
            _all_results = []

            for _algo, _algo_lbl in zip(algos, algo_labels):
                _lc_status_ph.caption(f"Treinando {_algo_lbl}…")
                _params = dict(params_per_algo.get(_algo, {}))

                # HPO
                if hpo_mode == "Optuna (automático)":
                    _prog = st.progress(0.0, text=f"Optuna — {_algo_lbl}…")
                    def _opt_cb(done, total, best, _p=_prog, _l=_algo_lbl):
                        _p.progress(done / total,
                                    text=f"Optuna {_l}: {done}/{total} — AUC {best:.4f}")
                    _params = optimize_hyperparams(
                        X_train, y_train, algorithm=_algo,
                        n_trials=n_trials, n_folds=_hpo_folds,
                        balancing=balancing, treatment=treatment,
                        progress_callback=_opt_cb,
                    )
                    _prog.progress(1.0, text=f"Optuna {_algo_lbl} concluído")

                elif hpo_mode == "Random Search":
                    _prog = st.progress(0.0, text=f"Random Search — {_algo_lbl}…")
                    def _rs_cb(done, total, best, _p=_prog, _l=_algo_lbl):
                        _p.progress(1.0, text=f"Random Search {_l} — AUC {best:.4f}")
                    with st.spinner(f"Random Search: {_algo_lbl}…"):
                        _params = random_search(
                            X_train, y_train, algorithm=_algo,
                            n_iter=n_iter, n_folds=_hpo_folds,
                            balancing=balancing, treatment=treatment,
                            progress_callback=_rs_cb,
                        )
                    _prog.progress(1.0, text=f"Random Search {_algo_lbl} concluído")

                elif hpo_mode == "Grid Search":
                    with st.spinner(f"Grid Search — {_algo_lbl}…"):
                        _params = grid_search(
                            X_train, y_train, algorithm=_algo,
                            n_folds=_hpo_folds, balancing=balancing,
                            treatment=treatment,
                        )

                # Treino
                import numpy as _np
                from sklearn.metrics import (
                    roc_auc_score as _rauc, average_precision_score as _ap,
                    f1_score as _f1, precision_score as _prec,
                    recall_score as _rec, brier_score_loss as _brier,
                )
                if val_strategy == "Validação cruzada (k-fold)":
                    with st.spinner(f"Treinando {_algo_lbl} · {n_folds}-fold CV…"):
                        _r = train_cv(
                            X=X_train, y=y_train, algorithm=_algo,
                            params=_params, n_folds=n_folds, balancing=balancing,
                            treatment=treatment,
                        )
                        _r["validation_strategy"] = "cv"
                elif val_strategy == "Validação Temporal":
                    with st.spinner(f"Treinando {_algo_lbl} · corte temporal {temporal_cutoff}…"):
                        import pandas as _pd_t
                        _dates = _pd_t.to_datetime(cohort[temporal_date_col], errors="coerce")
                        _cutoff_ts = _pd_t.Timestamp(temporal_cutoff)
                        _train_mask = _dates < _cutoff_ts
                        _test_mask  = _dates >= _cutoff_ts
                        if _train_mask.sum() < 10 or _test_mask.sum() < 5:
                            st.error(
                                f"Split temporal insuficiente: treino={_train_mask.sum()}, "
                                f"teste={_test_mask.sum()}. Ajuste a data de corte."
                            )
                            st.stop()
                        X_tr = X_train[_train_mask.values]
                        y_tr = y_train[_train_mask.values]
                        X_te = X_train[_test_mask.values]
                        y_te = y_train[_test_mask.values]
                        _pipe = build_pipeline(X_tr, _algo, _params, balancing=balancing, treatment=treatment)
                        _pipe.fit(X_tr, y_tr)
                        _te_probs = _pipe.predict_proba(X_te)[:, 1]
                        _te_preds = (_te_probs >= 0.5).astype(int)
                        _m = {
                            "roc_auc": float(_rauc(y_te, _te_probs)),
                            "pr_auc": float(_ap(y_te, _te_probs)),
                            "f1": float(_f1(y_te, _te_preds, zero_division=0)),
                            "precision": float(_prec(y_te, _te_preds, zero_division=0)),
                            "recall": float(_rec(y_te, _te_preds, zero_division=0)),
                            "brier": float(_brier(y_te, _te_probs)),
                            "fold": 1,
                        }
                        _final = build_pipeline(X_train, _algo, _params, balancing=balancing, treatment=treatment)
                        _final.fit(X_train, y_train)
                        _imp = {}
                        if hasattr(_final[-1], "feature_importances_"):
                            _imp = dict(zip(X_train.columns, _final[-1].feature_importances_))
                        _r = {
                            "fold_metrics": [_m],
                            "mean_metrics": {k: v for k, v in _m.items() if k != "fold"},
                            "oof_probs": _te_probs,
                            "y_eval": y_te.values,
                            "feature_importances": _imp,
                            "model": _final,
                            "X_columns": X_train.columns.tolist(),
                            "algorithm": _algo,
                            "validation_strategy": "temporal",
                            "temporal_date_col": temporal_date_col,
                            "temporal_cutoff": temporal_cutoff,
                        }
                else:
                    with st.spinner(f"Treinando {_algo_lbl} · holdout {holdout_size:.0%}…"):
                        X_tr, X_te, y_tr, y_te = train_test_split(
                            X_train, y_train, test_size=holdout_size,
                            stratify=y_train, random_state=42,
                        )
                        _pipe = build_pipeline(X_tr, _algo, _params, balancing=balancing, treatment=treatment)
                        _pipe.fit(X_tr, y_tr)
                        _te_probs = _pipe.predict_proba(X_te)[:, 1]
                        _te_preds = (_te_probs >= 0.5).astype(int)
                        _m = {
                            "roc_auc": float(_rauc(y_te, _te_probs)),
                            "pr_auc": float(_ap(y_te, _te_probs)),
                            "f1": float(_f1(y_te, _te_preds, zero_division=0)),
                            "precision": float(_prec(y_te, _te_preds, zero_division=0)),
                            "recall": float(_rec(y_te, _te_preds, zero_division=0)),
                            "brier": float(_brier(y_te, _te_probs)),
                            "fold": 1,
                        }
                        _final = build_pipeline(X_train, _algo, _params, balancing=balancing, treatment=treatment)
                        _final.fit(X_train, y_train)
                        _imp = {}
                        if hasattr(_final[-1], "feature_importances_"):
                            _imp = dict(zip(X_train.columns, _final[-1].feature_importances_))
                        _r = {
                            "fold_metrics": [_m],
                            "mean_metrics": {k: v for k, v in _m.items() if k != "fold"},
                            "oof_probs": _te_probs,
                            "y_eval": y_te.values,
                            "feature_importances": _imp,
                            "model": _final,
                            "X_columns": X_train.columns.tolist(),
                            "algorithm": _algo,
                            "validation_strategy": "holdout",
                            "holdout_size": holdout_size,
                        }

                _r["sample_n"] = len(X_train)
                _r["best_params"] = _params
                _r["hpo_mode"] = hpo_mode
                _r["algo_label"] = _algo_lbl
                _all_results.append(_r)

            # ── Melhor resultado ──────────────────────────────────────────────
            _best = max(_all_results, key=lambda r: r["mean_metrics"]["roc_auc"])
            _best["all_results"] = _all_results
            _lc_status_ph.caption(
                f"Concluído. Melhor: {_best.get('algo_label', '')} — AUC {_best['mean_metrics']['roc_auc']:.4f}"
            )
            ss["model_results"] = _best
            ss["active_sections"] = set()
            st.rerun()
        except Exception as e:
            st.error(f"Erro no treino: {e}")
            st.exception(e)
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 7 — RESULTADOS
# ═════════════════════════════════════════════════════════════════════════════
step_title(7, "Resultados do Modelo",
           "Métricas de desempenho, curvas ROC/PR, explicabilidade SHAP e exportação.")

ev = _ev()
results = ss["model_results"]

# ── Comparação de algoritmos (quando múltiplos foram treinados) ───────────────
_all = results.get("all_results", [])
if len(_all) > 1:
    st.markdown("#### Comparação de Algoritmos")
    _comp_df = pd.DataFrame([
        {
            "Algoritmo": r.get("algo_label", r.get("algorithm", "?").upper()),
            "ROC-AUC":        round(r["mean_metrics"]["roc_auc"], 4),
            "Sensibilidade":  round(r["mean_metrics"].get("recall", 0), 4),
            "Especificidade": round(r["mean_metrics"].get("specificity", 0), 4),
            "PR-AUC":         round(r["mean_metrics"]["pr_auc"], 4),
            "F1":             round(r["mean_metrics"]["f1"], 4),
        }
        for r in _all
    ]).sort_values("ROC-AUC", ascending=False).reset_index(drop=True)
    st.dataframe(_comp_df, use_container_width=True, hide_index=True)
    st.caption(
        f"Detalhes abaixo referentes ao melhor modelo: "
        f"**{results.get('algo_label', results.get('algorithm', '').upper())}**"
        f" (ROC-AUC {results['mean_metrics']['roc_auc']:.4f})"
    )
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

if len(_all) <= 1:
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── Toggle pills ─────────────────────────────────────────────────────────────
_sec_keys   = ["curvas", "distribuicao", "shap_global", "shap_individual", "metricas_clinicas", "equidade"]
_sec_labels = ["Curvas ROC/PR", "Distribuição", "SHAP Global",
               "SHAP Individual", "Métricas Clínicas", "Equidade"]
if "active_sections" not in ss:
    ss["active_sections"] = set()
_pill_cols = st.columns(len(_sec_keys))
for _pi, (_pk, _pl) in enumerate(zip(_sec_keys, _sec_labels)):
    with _pill_cols[_pi]:
        _active = _pk in ss["active_sections"]
        if st.button(_pl, key=f"pill_{_pk}",
                     type="primary" if _active else "secondary",
                     use_container_width=True):
            _secs = set(ss["active_sections"])
            if _pk in _secs:
                _secs.discard(_pk)
            else:
                _secs.add(_pk)
            ss["active_sections"] = _secs
            st.rerun()

m = results["mean_metrics"]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("ROC-AUC",        f"{m['roc_auc']:.4f}")
c2.metric("Sensibilidade",  f"{m.get('recall', 0):.4f}")
c3.metric("Especificidade", f"{m.get('specificity', 0):.4f}")
c4.metric("PR-AUC",         f"{m['pr_auc']:.4f}")
c5.metric("F1-Score",       f"{m['f1']:.4f}")

col_exp1, col_exp2 = st.columns(2)
with col_exp1:
    _vs_r = results.get("validation_strategy", "cv")
    _exp_label = ("Métricas por fold" if _vs_r == "cv"
                  else "Métricas do corte temporal" if _vs_r == "temporal"
                  else "Métricas do conjunto de teste")
    with st.expander(_exp_label):
        st.dataframe(ev.fold_metrics_table(results["fold_metrics"]), use_container_width=True, hide_index=True)
with col_exp2:
    with st.expander("Hiperparâmetros utilizados"):
        bp = results.get("best_params") or {}
        if bp:
            st.json(bp)
        else:
            st.caption("Parâmetros padrão (sem configuração explícita).")
        if results.get("sample_n"):
            sn = results["sample_n"]
            st.caption(f"Treinado com {sn:,} registros (amostra estratificada).")
        if results.get("hpo_mode") == "Optuna (automático)":
            st.caption("Hiperparâmetros encontrados via otimização bayesiana (Optuna).")

X_res = X[results["X_columns"]]
oof = results["oof_probs"]
# Holdout/Temporal: usar apenas os labels do conjunto de teste
if results.get("validation_strategy") in ("holdout", "temporal"):
    y_arr = results["y_eval"]
else:
    y_arr = y.values

if "curvas" in ss.get("active_sections", set()):
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
    st.markdown("**Curvas de desempenho**")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(ev.roc_chart(y_arr, oof), use_container_width=True)
    with col2:
        st.plotly_chart(ev.pr_chart(y_arr, oof), use_container_width=True)
    st.plotly_chart(ev.calibration_chart(y_arr, oof), use_container_width=True)

if "distribuicao" in ss.get("active_sections", set()):
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
    st.markdown("**Distribuição dos scores preditos**")
    fig_dist = px.histogram(
        x=oof, color=y_arr.astype(str), nbins=50, barmode="overlay", opacity=0.65,
        labels={"x": "Score predito", "color": "Desfecho real"},
        color_discrete_map={"0": "#3b82f6", "1": "#ef4444"},
        title="Scores por classe real",
    )
    fig_dist.update_layout(margin=dict(t=40, b=0))
    st.plotly_chart(fig_dist, use_container_width=True)

if "shap_global" in ss.get("active_sections", set()):
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
    st.markdown("**SHAP — Explicabilidade Global**")
    if results.get("feature_importances"):
        st.plotly_chart(ev.importance_chart(results["feature_importances"]), use_container_width=True)
    with st.spinner("Calculando SHAP…"):
        shap_fig = ev.shap_summary(results["model"], X_res.head(500))
    if shap_fig:
        st.plotly_chart(shap_fig, use_container_width=True)
    else:
        st.info("SHAP indisponível para este algoritmo.")

if "shap_individual" in ss.get("active_sections", set()):
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
    st.markdown("**SHAP — Explicabilidade Individual**")
    st.caption("Selecione um caso para ver a contribuição de cada variável na predição.")
    case_idx = st.number_input("Índice do caso", min_value=0, max_value=len(X_res) - 1,
                                value=0, step=1)
    with st.spinner("Calculando SHAP individual…"):
        wf_fig = ev.shap_waterfall_chart(results["model"], X_res, int(case_idx))
    if wf_fig:
        st.plotly_chart(wf_fig, use_container_width=True)
    else:
        st.info("SHAP individual indisponível para este algoritmo.")

if "metricas_clinicas" in ss.get("active_sections", set()):
    import plotly.graph_objects as _go
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
    st.markdown("**Métricas Clínicas por Ponto de Corte**")
    st.plotly_chart(ev.threshold_curve_chart(y_arr, oof), use_container_width=True)
    _mc_left, _mc_right = st.columns([3, 2])
    with _mc_left:
        threshold = st.slider(
            "Threshold", 0.01, 0.99, 0.50, 0.01,
            help="Ponto de corte para classificar como positivo (alto risco).",
        )
        tm = ev.threshold_metrics(y_arr, oof, threshold)
        _cm_fig = _go.Figure(_go.Heatmap(
            z=[[tm["tn"], tm["fp"]], [tm["fn"], tm["tp"]]],
            x=["Pred Negativo", "Pred Positivo"],
            y=["Real Negativo", "Real Positivo"],
            text=[[tm["tn"], tm["fp"]], [tm["fn"], tm["tp"]]],
            texttemplate="%{text}",
            colorscale=[[0, "#f0fdf4"], [1, "#166534"]],
            showscale=False,
        ))
        _cm_fig.update_layout(
            title="Matriz de confusão",
            height=240, margin=dict(t=40, b=10, l=10, r=10),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(_cm_fig, use_container_width=True)
    with _mc_right:
        st.markdown("")
        st.metric("Sensibilidade", f"{tm['sensitivity']:.1%}")
        st.metric("Especificidade", f"{tm['specificity']:.1%}")
        st.metric("VPP", f"{tm['ppv']:.1%}")
        st.metric("VPN", f"{tm['npv']:.1%}")
        st.metric("NNT", f"{tm['nnt']:.1f}" if tm["nnt"] < 999 else ">999")

if "equidade" in ss.get("active_sections", set()):
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
    st.markdown("**Análise de Equidade por Subgrupo**")
    _fairness_candidates = ["SEXO", "RACA_COR", "UF_ZI", "UF_NASC", "MUNIC_RES"]
    _fairness_cols = [c for c in _fairness_candidates if c in cohort.columns]
    if _fairness_cols:
        group_col = st.selectbox("Estratificar por", _fairness_cols,
                                  help="Analisa se o modelo performa igualmente para diferentes grupos.")
        _groups = cohort.loc[X_res.index, group_col].reset_index(drop=True)
        sub_df = ev.subgroup_metrics_table(y_arr, oof, _groups)
        if not sub_df.empty:
            st.dataframe(sub_df, use_container_width=True, hide_index=True)
            fig_eq = px.bar(
                sub_df, x="Subgrupo", y="ROC-AUC",
                color="ROC-AUC", color_continuous_scale="RdYlGn",
                range_color=[0.5, 1.0], title=f"ROC-AUC por {group_col}",
                text="ROC-AUC",
            )
            fig_eq.update_traces(textposition="outside")
            fig_eq.update_layout(height=360, showlegend=False)
            st.plotly_chart(fig_eq, use_container_width=True)
        else:
            st.info("Nenhum subgrupo com dados suficientes (mín. 20 casos e eventos positivos).")
    else:
        st.info("Nenhuma variável demográfica encontrada na coorte (SEXO, RACA_COR, UF).")

st.markdown("#### Exportar predições")
export_df = pd.DataFrame({
    "score": oof,
    "predicao": (oof >= 0.5).astype(int),
    "real": y_arr,
})
st.download_button(
    label="Baixar predições OOF (CSV)",
    data=export_df.to_csv(index=False).encode("utf-8"),
    file_name=f"predicoes_{ss['outcome_key']}.csv",
    mime="text/csv",
)

st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
st.markdown('<p class="ds-section-caption">Modelo treinado. Continue para calibração e benchmark, ou vá direto para inferência individual.</p>',
            unsafe_allow_html=True)
_btn_col1, _btn_spacer, _btn_col2 = st.columns([2, 3, 2])
with _btn_col1:
    if st.button("→ Calibração e Benchmark", type="primary", use_container_width=True):
        st.switch_page("pages/calibracao.py")
with _btn_col2:
    if st.button("→ Deploy — Inferência Individual", type="secondary", use_container_width=True):
        st.switch_page("pages/deploy.py")

st.markdown('</div>', unsafe_allow_html=True)
