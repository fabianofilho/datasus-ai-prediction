"""DataSUS AI Prediction — wizard completo (carregado sob demanda)."""
from __future__ import annotations

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
    from core.models.pipeline import ALGORITHMS, train_cv, optimize_hyperparams, calibrate_model, build_pipeline
    return ALGORITHMS, train_cv, optimize_hyperparams, calibrate_model, build_pipeline

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
[data-testid="stSidebar"], [data-testid="collapsedControl"],
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
  padding-left:   48px !important;
  padding-right:  48px !important;
  max-width:      1100px !important;
  margin:         0 auto !important;
}

/* ── Topbar ─────────────────────────────────────────────────── */
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
.ds-topbar-logo:hover { color: #374151 !important; }
.ds-topbar-badge {
  background: var(--fg); color: #fff;
  font-size: 0.62rem; font-weight: 700;
  padding: 2px 7px; border-radius: 4px;
  letter-spacing: .06em; text-transform: uppercase;
}
.ds-topbar-right { font-size: 0.78rem; color: var(--muted); }

/* ── Step bar ───────────────────────────────────────────────── */
.ds-stepbar {
  display: flex; align-items: center; gap: 4px; flex-wrap: wrap;
  margin-bottom: 28px;
  padding: 10px 0; border-bottom: 1px solid var(--border);
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
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
ss = st.session_state
_defaults: dict = {
    "outcome_key": None,
    "raw_data": {},
    "cohort": None,
    "model_config": None,
    "model_results": None,
    "calib_results": None,
    "comparison_results": [],
    "sel_states": ["SP"],
    "sel_years": [2023],
    "manual_needed": [],
    "sample_n": 10_000,
    "sample_seed": 42,
}
for k, v in _defaults.items():
    if k not in ss:
        ss[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────────
def current_step() -> int:
    if ss.get("comparison_results"):
        return 8
    if ss.get("calib_results"):
        return 7
    if ss["model_results"]:
        return 6
    if ss.get("model_config"):
        return 5
    if ss["cohort"] is not None:
        return 4
    if ss["raw_data"]:
        return 3
    if ss["outcome_key"]:
        return 2
    return 1


def render_topbar() -> None:
    st.markdown(
        '<div class="ds-topbar">'
        '<a class="ds-topbar-logo" href="/" target="_self">'
        '<span class="ms" style="font-size:1.2rem;color:#111827">local_hospital</span>'
        'DataSUS AI'
        '<span class="ds-topbar-badge">PREDICTION</span>'
        '</a>'
        '<div class="ds-topbar-right">Modelagem preditiva em saúde pública</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_step_bar(step: int) -> None:
    labels = ["Desfecho", "Dados", "Coorte", "Modelo", "Treinamento", "Resultados", "Calibração", "Benchmark"]
    optionals = {7, 8}
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


# ── Topbar + wrapper ──────────────────────────────────────────────────────────
render_topbar()
st.markdown('<div class="ds-page">', unsafe_allow_html=True)
render_step_bar(current_step())
st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 1 — DESFECHO
# ═════════════════════════════════════════════════════════════════════════════
if ss["outcome_key"]:
    o = OUTCOMES[ss["outcome_key"]]
    done_bar(
        f'<strong>{o.name}</strong> &nbsp;·&nbsp; {", ".join(o.data_sources)}',
        "chg_outcome",
        ["outcome_key", "raw_data", "cohort", "model_config", "model_results", "manual_needed"],
    )
else:
    step_title(1, "Selecionar Desfecho",
               "Escolha o desfecho clínico que deseja predizer. Organizado por área temática.")
    for group_name, keys in OUTCOME_GROUPS.items():
        st.markdown(f'<p class="ds-group-label">{group_name}</p>', unsafe_allow_html=True)
        cols = st.columns(min(len(keys), 3))
        for i, key in enumerate(keys):
            outcome = OUTCOMES.get(key)
            if not outcome:
                continue
            with cols[i % 3]:
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
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # ETAPA 2 — DADOS
    # ═════════════════════════════════════════════════════════════════════════
    if ss["raw_data"]:
        summary = " &nbsp;·&nbsp; ".join(
            f"{src}: <strong>{len(df):,}</strong>" for src, df in ss["raw_data"].items()
        )
        done_bar(summary, "chg_data",
                 ["raw_data", "cohort", "model_config", "model_results", "manual_needed"])
        with st.expander("Ver preview dos dados"):
            for src, df in ss["raw_data"].items():
                st.caption(f"**{src}** — {len(df):,} registros, {df.shape[1]} colunas")
                st.dataframe(df.head(8), use_container_width=True)
    else:
        step_title(2, "Baixar Dados",
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
                    help="Limita o download para evitar falta de memória. Padrão: 10.000. Use 500.000 para dados completos.",
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

    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

    # ── Lazy: CohortBuilder (só carrega ao chegar na etapa 3) ────────────────
    CohortBuilder = _cohort()

    # ═════════════════════════════════════════════════════════════════════════
    # ETAPA 3 — COORTE
    # ═════════════════════════════════════════════════════════════════════════
    step_title(3, "Construir Coorte",
               "Filtra casos elegíveis, cria features e define o target para o modelo.")
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

# ─── COHORT BUILT: Steps 4-6 ────────────────────────────────────────────────
st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── Lazy: CohortBuilder e pipeline ML ────────────────────────────────────────
CohortBuilder = _cohort()
ALGORITHMS, train_cv, optimize_hyperparams, calibrate_model, build_pipeline = _pipeline()

cohort = ss["cohort"]
builder = CohortBuilder(outcome)
X, y = builder.get_Xy(cohort)

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 4 — CONFIGURAR MODELO
# ═════════════════════════════════════════════════════════════════════════════
if ss.get("model_config"):
    cfg = ss["model_config"]
    _n_feat = len(cfg["selected_features"])
    _val_short = (
        f"{cfg['n_folds']}-fold CV"
        if cfg["val_strategy"] == "Validação cruzada (k-fold)"
        else f"Holdout {cfg['holdout_size']:.0%}"
    )
    done_bar(
        f'<strong>{cfg["algo_label"]}</strong> &nbsp;·&nbsp; {_val_short} &nbsp;·&nbsp; {_n_feat} features',
        "chg_model_config",
        ["model_config", "model_results", "calib_results", "comparison_results"],
    )
else:
    step_title(4, "Configurar Modelo",
               "Configure o algoritmo, validação e hiperparâmetros.")
    bal = builder.class_balance(cohort)
    total_n = bal["total"]
    st.info(
        f"**{total_n:,}** registros · prevalência **{bal['prevalence']:.1%}** · "
        f"**{len(X.columns)}** features disponíveis"
    )

    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Algoritmo e validação**")
        algo_label = st.selectbox("Algoritmo", list(ALGORITHMS.keys()))
        algo = ALGORITHMS[algo_label]
        val_strategy = st.radio(
            "Estratégia de validação",
            ["Validação cruzada (k-fold)", "Holdout (train/test)"],
            horizontal=True,
        )
        if val_strategy == "Validação cruzada (k-fold)":
            n_folds = st.slider("Folds", 3, 10, 5)
            holdout_size = 0.20
        else:
            holdout_size = st.select_slider(
                "Proporção de teste",
                options=[0.10, 0.15, 0.20, 0.25, 0.30],
                value=0.20,
                format_func=lambda x: f"{x:.0%}",
            )
            n_folds = 1
        use_smote = st.checkbox("SMOTE — oversample da classe minoritária",
                                help="Recomendado quando prevalência < 5%")
        st.markdown("**Modo de hiperparâmetros**")
        hpo_mode = st.radio("Modo", ["Manual", "Optuna (automático)"],
                            horizontal=True, label_visibility="collapsed")
        n_trials = (
            st.slider("Tentativas (trials)", 10, 200, 50, 10) if hpo_mode == "Optuna (automático)" else 50
        )
    with c2:
        if hpo_mode == "Manual":
            st.markdown("**Hiperparâmetros**")
            params: dict = {}
            if algo in ("lgbm", "xgb", "rf"):
                params["n_estimators"] = st.slider("Árvores (n_estimators)", 50, 1000, 300, 50)
            if algo in ("lgbm", "xgb"):
                params["learning_rate"] = st.select_slider(
                    "Learning rate", [0.005, 0.01, 0.02, 0.05, 0.1, 0.2], value=0.05)
            if algo in ("lgbm", "xgb", "rf"):
                params["max_depth"] = st.slider("max_depth (−1 = sem limite)", -1, 15, -1)
            if algo == "logreg":
                params["C"] = st.select_slider("C (regularização)", [0.001, 0.01, 0.1, 1.0, 10.0], value=1.0)
        else:
            params = {}
            st.caption("Optuna buscará automaticamente os melhores hiperparâmetros.")

    selected_features = st.multiselect(
        "Features para o modelo", X.columns.tolist(), default=X.columns.tolist(),
    )
    if not selected_features:
        st.warning("Selecione pelo menos uma feature.")
        st.stop()

    if st.button("Confirmar Configuração", type="primary"):
        ss["model_config"] = {
            "algo": algo,
            "algo_label": algo_label,
            "val_strategy": val_strategy,
            "n_folds": n_folds,
            "holdout_size": holdout_size,
            "use_smote": use_smote,
            "hpo_mode": hpo_mode,
            "n_trials": n_trials,
            "params": params,
            "selected_features": selected_features,
        }
        ss["model_results"] = None
        ss["calib_results"] = None
        ss["comparison_results"] = []
        st.rerun()
    st.stop()

st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 5 — TREINAR
# ═════════════════════════════════════════════════════════════════════════════
cfg = ss["model_config"]
algo = cfg["algo"]
algo_label = cfg["algo_label"]
val_strategy = cfg["val_strategy"]
n_folds = cfg["n_folds"]
holdout_size = cfg["holdout_size"]
use_smote = cfg["use_smote"]
hpo_mode = cfg["hpo_mode"]
n_trials = cfg["n_trials"]
params = cfg["params"]
selected_features = cfg["selected_features"]

if ss["model_results"]:
    results = ss["model_results"]
    m = results["mean_metrics"]
    sample_info = ""
    if results.get("sample_n") and results["sample_n"] < len(cohort):
        sample_info = f' &nbsp;·&nbsp; amostra <strong>{results["sample_n"]:,}</strong>'
    hpo_tag = " · Optuna" if results.get("hpo_mode") == "Optuna (automático)" else ""
    if results.get("validation_strategy") == "holdout":
        val_tag = f' · Holdout {results.get("holdout_size", 0.2):.0%}'
    else:
        val_tag = ""
    done_bar(
        f'<strong>{results["algorithm"].upper()}</strong>{hpo_tag}{val_tag} &nbsp;·&nbsp; '
        f'AUC <strong>{m["roc_auc"]:.3f}</strong> &nbsp;·&nbsp; '
        f'F1 <strong>{m["f1"]:.3f}</strong> &nbsp;·&nbsp; '
        f'PR-AUC <strong>{m["pr_auc"]:.3f}</strong>{sample_info}',
        "chg_model",
        ["model_results", "calib_results", "comparison_results"],
    )
else:
    step_title(5, "Treinar Modelo",
               "Execute o treinamento com a configuração selecionada.")
    bal = builder.class_balance(cohort)
    total_n = bal["total"]
    _val_tag_label = (
        f"{n_folds}-fold CV" if val_strategy == "Validação cruzada (k-fold)"
        else f"Holdout {holdout_size:.0%}"
    )
    st.info(
        f"**{algo_label}** · {_val_tag_label} · **{len(selected_features)}** features · "
        f"**{total_n:,}** registros"
        + (" · SMOTE" if use_smote else "")
        + (f" · Optuna {n_trials} trials" if hpo_mode == "Optuna (automático)" else "")
    )

    X_model = X[selected_features]
    sample_n = total_n

    def _lc_fig(sizes, val_aucs, train_aucs):
        import plotly.graph_objects as _go
        fig = _go.Figure()
        if sizes:
            fig.add_trace(_go.Scatter(
                x=sizes, y=val_aucs, mode="lines+markers", name="Validação",
                line=dict(color="#1a56db", width=2.5), marker=dict(size=9),
                fill="tozeroy", fillcolor="rgba(26,86,219,0.07)",
            ))
            if train_aucs:
                fig.add_trace(_go.Scatter(
                    x=sizes, y=train_aucs, mode="lines+markers", name="Treino",
                    line=dict(color="#94a3b8", width=1.5, dash="dot"), marker=dict(size=6),
                ))
        fig.update_layout(
            title="Curva de Aprendizado — ROC-AUC por volume de dados",
            xaxis_title="Registros de treinamento",
            yaxis=dict(title="ROC-AUC", range=[0.45, 1.0], gridcolor="rgba(0,0,0,0.07)"),
            xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.07)", zeroline=False),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=320,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=60, b=40, l=60, r=20),
        )
        return fig

    _lc_chart_ph = st.empty()
    _lc_status_ph = st.empty()
    _lc_chart_ph.plotly_chart(_lc_fig([], [], []), use_container_width=True)

    btn_label = (
        f"Otimizar + Treinar {algo_label} · {_val_tag_label}"
        if hpo_mode == "Optuna (automático)"
        else f"Treinar {algo_label} · {_val_tag_label}"
    )

    if st.button(btn_label, type="primary"):
        try:
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import roc_auc_score as _roc_auc

            X_train = X_model
            y_train = y
            if sample_n < total_n:
                X_train, _, y_train, _ = train_test_split(
                    X_train, y_train, train_size=int(sample_n),
                    stratify=y_train, random_state=42,
                )

            # ── Learning curve ────────────────────────────────────────────────
            _lc_sizes, _lc_val, _lc_tr = [], [], []
            _fracs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
            try:
                _X_lc, _X_hold, _y_lc, _y_hold = train_test_split(
                    X_train, y_train, test_size=0.2, stratify=y_train, random_state=42,
                )
            except Exception:
                _X_lc, _X_hold = X_train, X_train
                _y_lc, _y_hold = y_train, y_train

            for _frac in _fracs:
                _n = max(30, int(len(_X_lc) * _frac))
                try:
                    if _frac < 1.0:
                        _Xs, _, _ys, _ = train_test_split(
                            _X_lc, _y_lc, train_size=_n, stratify=_y_lc, random_state=42,
                        )
                    else:
                        _Xs, _ys = _X_lc, _y_lc
                    _qp = build_pipeline(_Xs, algo, params, use_smote=False)
                    _qp.fit(_Xs, _ys)
                    _tr_auc = float(_roc_auc(_ys, _qp.predict_proba(_Xs)[:, 1])) if _ys.sum() > 0 else 0.5
                    _vl_auc = float(_roc_auc(_y_hold, _qp.predict_proba(_X_hold)[:, 1])) if _y_hold.sum() > 0 else 0.5
                except Exception:
                    _tr_auc = _vl_auc = 0.5
                _lc_sizes.append(_n)
                _lc_tr.append(_tr_auc)
                _lc_val.append(_vl_auc)
                _lc_chart_ph.plotly_chart(_lc_fig(_lc_sizes, _lc_val, _lc_tr), use_container_width=True)
                _lc_status_ph.caption(
                    f"Fração {int(_frac*100)}% — {_n:,} registros — Val AUC: {_vl_auc:.3f}"
                )

            _lc_status_ph.caption("Finalizando treino…")

            # ── Optuna HPO ────────────────────────────────────────────────────
            if hpo_mode == "Optuna (automático)":
                prog = st.progress(0.0, text="Iniciando Optuna…")

                def _optuna_cb(done, total, best):
                    prog.progress(done / total,
                                  text=f"Optuna: trial {done}/{total} — melhor ROC-AUC {best:.4f}")

                _hpo_folds = min(n_folds, 3) if val_strategy == "Validação cruzada (k-fold)" else 3
                params = optimize_hyperparams(
                    X_train, y_train, algorithm=algo,
                    n_trials=n_trials, n_folds=_hpo_folds,
                    use_smote=use_smote, progress_callback=_optuna_cb,
                )
                prog.progress(1.0, text=f"Optuna concluído — {n_trials} trials")

            # ── Treino final ──────────────────────────────────────────────────
            if val_strategy == "Validação cruzada (k-fold)":
                with st.spinner(f"Treinando {algo_label} com {n_folds}-fold CV…"):
                    results = train_cv(
                        X=X_train, y=y_train, algorithm=algo,
                        params=params, n_folds=n_folds, use_smote=use_smote,
                    )
                    results["validation_strategy"] = "cv"
            else:
                with st.spinner(f"Treinando {algo_label} — holdout {holdout_size:.0%}…"):
                    import numpy as _np
                    from sklearn.metrics import (
                        roc_auc_score as _rauc, average_precision_score as _ap,
                        f1_score as _f1, precision_score as _prec,
                        recall_score as _rec, brier_score_loss as _brier,
                    )
                    X_tr, X_te, y_tr, y_te = train_test_split(
                        X_train, y_train, test_size=holdout_size,
                        stratify=y_train, random_state=42,
                    )
                    _pipe = build_pipeline(X_tr, algo, params, use_smote)
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
                    # Refit on full training set
                    _final = build_pipeline(X_train, algo, params, use_smote)
                    _final.fit(X_train, y_train)
                    _imp = {}
                    _m2 = _final[-1]
                    if hasattr(_m2, "feature_importances_"):
                        _imp = dict(zip(X_train.columns, _m2.feature_importances_))
                    results = {
                        "fold_metrics": [_m],
                        "mean_metrics": {k: v for k, v in _m.items() if k != "fold"},
                        "oof_probs": _te_probs,
                        "y_eval": y_te.values,
                        "feature_importances": _imp,
                        "model": _final,
                        "X_columns": X_train.columns.tolist(),
                        "algorithm": algo,
                        "validation_strategy": "holdout",
                        "holdout_size": holdout_size,
                    }

            results["sample_n"] = len(X_train)
            results["best_params"] = params
            results["hpo_mode"] = hpo_mode
            ss["model_results"] = results
            st.rerun()
        except Exception as e:
            st.error(f"Erro no treino: {e}")
            st.exception(e)
    st.stop()

st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 6 — RESULTADOS
# ═════════════════════════════════════════════════════════════════════════════
step_title(6, "Resultados do Modelo",
           "Métricas de desempenho, curvas ROC/PR, explicabilidade SHAP e exportação.")

ev = _ev()
results = ss["model_results"]

m = results["mean_metrics"]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("ROC-AUC", f"{m['roc_auc']:.4f}")
c2.metric("PR-AUC", f"{m['pr_auc']:.4f}")
c3.metric("F1-Score", f"{m['f1']:.4f}")
c4.metric("Recall", f"{m['recall']:.4f}")
c5.metric("Brier Score", f"{m['brier']:.4f}")

col_exp1, col_exp2 = st.columns(2)
with col_exp1:
    _exp_label = "Métricas por fold" if results.get("validation_strategy") != "holdout" else "Métricas do conjunto de teste"
    with st.expander(_exp_label):
        st.dataframe(ev.fold_metrics_table(results["fold_metrics"]), use_container_width=True)
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
# Holdout: usar apenas os labels do conjunto de teste
if results.get("validation_strategy") == "holdout":
    y_arr = results["y_eval"]
else:
    y_arr = y.values

st.markdown("#### Curvas de desempenho")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(ev.roc_chart(y_arr, oof), use_container_width=True)
with col2:
    st.plotly_chart(ev.pr_chart(y_arr, oof), use_container_width=True)

st.plotly_chart(ev.calibration_chart(y_arr, oof), use_container_width=False)

st.markdown("#### Distribuição dos scores preditos")
fig_dist = px.histogram(
    x=oof, color=y_arr.astype(str), nbins=50, barmode="overlay", opacity=0.65,
    labels={"x": "Score predito", "color": "Desfecho real"},
    color_discrete_map={"0": "#3b82f6", "1": "#ef4444"},
    title="Scores por classe real",
)
fig_dist.update_layout(margin=dict(t=40, b=0))
st.plotly_chart(fig_dist, use_container_width=True)

if results.get("feature_importances"):
    st.markdown("#### Importância das variáveis")
    st.plotly_chart(ev.importance_chart(results["feature_importances"]), use_container_width=False)

st.markdown("#### SHAP — Explicabilidade Global")
with st.spinner("Calculando SHAP…"):
    shap_fig = ev.shap_summary(results["model"], X_res.head(500))
if shap_fig:
    st.plotly_chart(shap_fig, use_container_width=False)
else:
    st.info("SHAP indisponível para este algoritmo.")

# ── SHAP Local ────────────────────────────────────────────────────────────────
st.markdown("#### SHAP — Explicabilidade Individual")
st.caption("Selecione um caso para ver a contribuição de cada variável na predição.")
case_idx = st.number_input("Índice do caso", min_value=0, max_value=len(X_res) - 1,
                            value=0, step=1)
with st.spinner("Calculando SHAP individual…"):
    wf_fig = ev.shap_waterfall_chart(results["model"], X_res, int(case_idx))
if wf_fig:
    st.plotly_chart(wf_fig, use_container_width=True)
else:
    st.info("SHAP individual indisponível para este algoritmo.")

# ── Métricas Clínicas por Threshold ──────────────────────────────────────────
st.markdown("#### Métricas Clínicas por Ponto de Corte")
st.plotly_chart(ev.threshold_curve_chart(y_arr, oof), use_container_width=True)
threshold = st.slider(
    "Threshold", 0.01, 0.99, 0.50, 0.01,
    help="Ponto de corte para classificar como positivo (alto risco).",
)
tm = ev.threshold_metrics(y_arr, oof, threshold)
mc1, mc2, mc3, mc4, mc5 = st.columns(5)
mc1.metric("Sensibilidade", f"{tm['sensitivity']:.1%}")
mc2.metric("Especificidade", f"{tm['specificity']:.1%}")
mc3.metric("VPP", f"{tm['ppv']:.1%}")
mc4.metric("VPN", f"{tm['npv']:.1%}")
mc5.metric("NNT", f"{tm['nnt']:.1f}" if tm["nnt"] < 999 else ">999")
with st.expander("Matriz de confusão"):
    cm_df = pd.DataFrame(
        [[tm["tn"], tm["fp"]], [tm["fn"], tm["tp"]]],
        index=["Real Negativo", "Real Positivo"],
        columns=["Pred Negativo", "Pred Positivo"],
    )
    st.dataframe(cm_df, use_container_width=False)

# ── Análise de Equidade por Subgrupo ─────────────────────────────────────────
st.markdown("#### Análise de Equidade por Subgrupo")
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
st.markdown('<p class="ds-section-caption">Modelo treinado. Continue para calibração e benchmark.</p>',
            unsafe_allow_html=True)
if st.button("→ Calibração e Benchmark", type="primary"):
    st.switch_page("pages/calibracao.py")

st.markdown('</div>', unsafe_allow_html=True)
