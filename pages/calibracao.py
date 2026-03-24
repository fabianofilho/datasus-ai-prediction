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
        '<a class="ds-topbar-right" href="/" target="_self">Calibração e Benchmark</a>'
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
            _cat_lbl = {"ohe": "One-Hot", "ordinal": "Ordinal", "target": "Target", "drop": "Remover"}.get(
                tc_.get("cat_default", "ohe"), "—")
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

if st.button("← Voltar aos Resultados", type="secondary"):
    st.switch_page("pages/analise.py")

step_title(8, "Benchmark entre Estados",  # step 8
           "Aplica o modelo treinado a novas coortes de outros estados e compara métricas e SHAP.")

if ss["comparison_results"]:
    comp = ss["comparison_results"]
    st.markdown("**Métricas por coorte**")
    st.dataframe(ev.metrics_comparison_table(comp), use_container_width=True, hide_index=True)

    shap_dicts = [r["shap_dict"] for r in comp if r.get("shap_dict")]
    shap_labels = [r["label"] for r in comp if r.get("shap_dict")]
    if len(shap_dicts) >= 2:
        st.markdown("**Comparação SHAP entre coortes**")
        st.plotly_chart(ev.shap_comparison_chart(shap_dicts, shap_labels), use_container_width=True)

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
        cmp_states = st.multiselect(
            "Estados para comparação",
            [s for s in STATES if s not in already_used],
            default=[],
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

        def _run_state_group(label: str, states: list[str], years: list[int], raw_override=None):
            try:
                if raw_override is not None:
                    raw = raw_override
                else:
                    raw = {}
                    for src in outcome.data_sources:
                        dfs = []
                        for st_ in states:
                            for yr in years:
                                dfs.append(fetch(src, st_, yr))
                        raw[src] = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

                builder_cmp = CohortBuilder(outcome)
                cohort_cmp = builder_cmp.build(raw)
                X_cmp, y_cmp = builder_cmp.get_Xy(cohort_cmp)

                train_cols = results["X_columns"]
                for col in train_cols:
                    if col not in X_cmp.columns:
                        X_cmp[col] = float("nan")
                X_cmp = X_cmp[train_cols]

                # Limita ao mesmo N do treino original para comparação justa
                _train_n = results.get("sample_n")
                if _train_n and len(X_cmp) > _train_n:
                    _idx = X_cmp.sample(n=_train_n, random_state=42).index
                    X_cmp = X_cmp.loc[_idx]
                    y_cmp = y_cmp.loc[_idx]

                # Separa pré-processamento do estimador final para evitar erros
                # de shape (pandas DataFrame→numpy) no Pipeline.predict_proba.
                # Aplica o ColumnTransformer diretamente (recebe DataFrame com
                # nomes de colunas) e passa numpy para o estimador final.
                import numpy as _np_bm
                _base_pipeline = results["model"]
                _prep_steps = _base_pipeline[:-1]   # tudo exceto o modelo final
                _clf_final   = _base_pipeline[-1]   # só o estimador final

                X_t = _prep_steps.transform(X_cmp)  # DataFrame → numpy (OHE expandido)
                if hasattr(X_t, "toarray"):
                    X_t = X_t.toarray()
                if hasattr(X_t, "values"):          # se ainda for DataFrame
                    X_t = X_t.values
                X_t = _np_bm.asarray(X_t, dtype=float)

                probs_cmp = _clf_final.predict_proba(X_t)[:, 1]
                preds_cmp = (probs_cmp >= 0.5).astype(int)

                from sklearn.metrics import (
                    roc_auc_score, average_precision_score,
                    f1_score, recall_score, brier_score_loss,
                )
                metrics_cmp = {
                    "roc_auc": roc_auc_score(y_cmp, probs_cmp),
                    "pr_auc": average_precision_score(y_cmp, probs_cmp),
                    "f1": f1_score(y_cmp, preds_cmp, zero_division=0),
                    "recall": recall_score(y_cmp, preds_cmp, zero_division=0),
                    "brier": brier_score_loss(y_cmp, probs_cmp),
                }
                shap_d = ev.shap_values_dict(_base_pipeline, X_cmp)
                return {"label": label, "n": len(y_cmp), "metrics": metrics_cmp, "shap_dict": shap_d}
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

st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
st.markdown('<p class="ds-section-caption">Prossiga para inferência individual ou exporte o relatório completo do pipeline.</p>',
            unsafe_allow_html=True)
_dep_l, _dep_r = st.columns(2)
with _dep_l:
    if st.button("→ Deploy", type="secondary", use_container_width=True):
        st.switch_page("pages/deploy.py")
with _dep_r:
    if st.button("→ Relatório Final", type="primary", use_container_width=True):
        st.switch_page("pages/relatorio.py")

st.markdown('</div>', unsafe_allow_html=True)
