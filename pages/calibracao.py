"""DataSUS AI Prediction — Calibracao e Benchmark (pagina separada)."""
from __future__ import annotations

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
[data-testid="stSidebar"], [data-testid="collapsedControl"],
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
  padding-left: 48px !important; padding-right: 48px !important;
  max-width: 1100px !important; margin: 0 auto !important;
}
.ds-topbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  height: var(--topbar-h); background: var(--bg);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 48px;
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
.ds-topbar-right { font-size: 0.78rem; color: var(--muted); }
.ds-stepbar {
  display: flex; align-items: center; gap: 4px; flex-wrap: wrap;
  margin-bottom: 28px; padding: 10px 0; border-bottom: 1px solid var(--border);
}
.ds-step {
  border-radius: 4px; padding: 3px 12px;
  font-size: 0.78rem; font-weight: 500; white-space: nowrap;
}
.ds-step-done   { color: var(--muted); }
.ds-step-active { background: var(--fg); color: #fff; font-weight: 600; }
.ds-step-locked { color: #d1d5db; }
.ds-step-optional { color: #d1d5db; }
.ds-step-arrow  { color: #d1d5db; font-size: 0.85rem; padding: 0 1px; }
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
[data-testid="stExpander"] {
  background: var(--bg) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; box-shadow: none !important;
}
.ds-page { display: contents; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
ss = st.session_state
_defaults: dict = {
    "outcome_key": None, "raw_data": {}, "cohort": None,
    "model_results": None, "calib_results": None, "comparison_results": [],
    "sel_states": ["SP"], "sel_years": [2023], "manual_needed": [],
    "sample_n": 10_000, "sample_seed": 42, "use_sample": True,
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
        '<div class="ds-topbar-right">Calibração e Benchmark</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_step_bar(step: int) -> None:
    labels = ["Desfecho", "Dados", "Coorte", "Modelo", "Resultados", "Calibração", "Benchmark"]
    optionals = {6, 7}
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
            st.rerun()


def step_title(n: int, title: str, caption: str = "") -> None:
    st.markdown(
        f'<p class="ds-section-title">Passo {n} — {title}</p>'
        + (f'<p class="ds-section-caption">{caption}</p>' if caption else ""),
        unsafe_allow_html=True,
    )


# ── Topbar ─────────────────────────────────────────────────────────────────────
render_topbar()
st.markdown('<div class="ds-page">', unsafe_allow_html=True)

# ── Guard: precisa ter modelo treinado ─────────────────────────────────────────
if not ss["model_results"] or not ss["outcome_key"] or ss["cohort"] is None:
    st.warning("Nenhum modelo treinado encontrado. Volte para a etapa de treinamento.")
    if st.button("← Voltar ao Modelo", type="primary"):
        st.switch_page("pages/analise.py")
    st.stop()

# ── Stepbar ────────────────────────────────────────────────────────────────────
_step = 7 if ss.get("comparison_results") else 6
render_step_bar(_step)
st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── Voltar ao modelo ───────────────────────────────────────────────────────────
if st.button("← Voltar ao Modelo", type="secondary"):
    st.switch_page("pages/analise.py")

st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

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

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 6 — CALIBRAÇÃO (opcional)
# ═════════════════════════════════════════════════════════════════════════════
step_title(6, "Calibração do Modelo",
           "Ajusta as probabilidades para que reflitam frequências reais. Opcional — pule se não necessário.")

if ss["calib_results"]:
    cr = ss["calib_results"]
    if cr.get("skipped"):
        st.info("Calibração pulada. O modelo original será usado no benchmark.")
    else:
        delta = cr["brier_delta"]
        delta_sign = "-" if delta >= 0 else "+"
        done_bar(
            f'Método <strong>{cr["method"].capitalize()}</strong> &nbsp;·&nbsp; '
            f'Brier antes <strong>{cr["brier_before"]:.4f}</strong> → '
            f'depois <strong>{cr["brier_after"]:.4f}</strong> &nbsp;·&nbsp; '
            f'melhora <strong>{delta_sign}{abs(delta):.4f}</strong>',
            "chg_calib",
            ["calib_results", "comparison_results"],
        )
        col_cal1, col_cal2 = st.columns(2)
        with col_cal1:
            st.plotly_chart(
                ev.calibration_comparison_chart(
                    cr["y_eval"], cr["raw_probs"], cr["cal_probs"],
                    method_label=f'Calibrado ({cr["method"]})',
                ),
                use_container_width=True,
            )
        with col_cal2:
            st.metric("Brier antes", f"{cr['brier_before']:.4f}")
            st.metric("Brier depois", f"{cr['brier_after']:.4f}",
                      delta=f"{-delta:+.4f}", delta_color="inverse")
            if delta > 0:
                st.success("Calibração melhorou as probabilidades.")
            elif delta < 0:
                st.warning("Calibração piorou levemente. Considere o método alternativo.")
            else:
                st.info("Sem variação significativa.")
else:
    c_col1, c_col2 = st.columns([2, 1])
    with c_col1:
        calib_method = st.radio(
            "Método de calibração",
            ["sigmoid", "isotonic"],
            format_func=lambda x: "Platt Scaling (sigmoid)" if x == "sigmoid" else "Isotonic Regression",
            horizontal=True,
            help=(
                "Platt Scaling: mais estável com pouco dado, assume forma sigmoide. "
                "Isotonic: mais flexível, requer pelo menos ~1.000 amostras."
            ),
        )
    with c_col2:
        st.caption(
            "A calibração usa 25% dos dados como holdout interno para ajustar "
            "as probabilidades sem vazar informação do treino."
        )
    col_cb1, col_cb2 = st.columns(2)
    with col_cb1:
        if st.button("Executar Calibração", type="primary"):
            with st.spinner("Executando calibração…"):
                try:
                    cr = calibrate_model(
                        results["model"], X_res, y, method=calib_method,
                    )
                    ss["calib_results"] = cr
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro na calibração: {e}")
    with col_cb2:
        if st.button("Pular calibração", type="secondary"):
            ss["calib_results"] = {"skipped": True, "cal_model": results["model"]}
            st.rerun()

st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 7 — BENCHMARK ENTRE ESTADOS (opcional)
# ═════════════════════════════════════════════════════════════════════════════
step_title(7, "Benchmark entre Estados",
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
        st.rerun()
else:
    st.info(
        "Selecione estados adicionais para comparar o desempenho do modelo "
        "treinado em populações diferentes."
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

                probs_cmp = _active_model.predict_proba(X_cmp)[:, 1]
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
                shap_d = ev.shap_values_dict(_active_model, X_cmp)
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

st.markdown('</div>', unsafe_allow_html=True)
