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
    from core.models.pipeline import ALGORITHMS, train_cv, optimize_hyperparams, calibrate_model
    return ALGORITHMS, train_cv, optimize_hyperparams, calibrate_model

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
<style>
/* ════════════════════════════════════════════════════════════════
   DESIGN SYSTEM — DataSUS AI  (baseado em review-ai-hub)
   ════════════════════════════════════════════════════════════════ */

/* ── Tokens ─────────────────────────────────────────────────── */
:root {
  --primary:        #1a56db;
  --primary-hover:  #1648c0;
  --primary-light:  #eff6ff;
  --primary-ring:   rgba(26,86,219,.22);
  --bg:             #ffffff;
  --bg-page:        #f0f4f8;
  --fg:             #1e2d4a;
  --muted:          #6b7d9b;
  --border:         #dce3ed;
  --success:        #059669;
  --success-bg:     #f0fdf4;
  --success-border: #bbf7d0;
  --radius:         8px;
  --topbar-h:       56px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,.08);
  --shadow-md: 0 4px 12px rgba(0,0,0,.10);
}

/* ── Oculta tudo nativo do Streamlit ────────────────────────── */
header, footer,
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarNav"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu { display: none !important; }

/* ── Base da página ─────────────────────────────────────────── */
html, body, .stApp,
[data-testid="stAppViewContainer"] {
  background: var(--bg-page) !important;
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif !important;
  color: var(--fg) !important;
}

/* ── Container do Streamlit ─────────────────────────────────── */
.block-container {
  padding-top:    calc(var(--topbar-h) + 28px) !important;
  padding-bottom: 56px !important;
  padding-left:   40px !important;
  padding-right:  40px !important;
  max-width:      1180px !important;
  margin:         0 auto !important;
}

/* ── Topbar fixo full-width ─────────────────────────────────── */
.ds-topbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 9999;
  height: var(--topbar-h);
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  box-shadow: var(--shadow-sm);
}
.ds-topbar-logo {
  display: flex; align-items: center; gap: 10px;
  font-size: 1rem; font-weight: 700; color: var(--fg);
  text-decoration: none;
}
.ds-topbar-badge {
  background: var(--primary); color: #fff;
  font-size: 0.68rem; font-weight: 700;
  padding: 2px 8px; border-radius: 20px;
  letter-spacing: .04em;
}
.ds-topbar-right { font-size: 0.8rem; color: var(--muted); }

/* ── Indicador de etapas ────────────────────────────────────── */
.ds-stepbar {
  display: flex; align-items: center;
  gap: 4px; flex-wrap: wrap;
  margin-bottom: 24px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 10px 16px;
  box-shadow: var(--shadow-sm);
}
.ds-step {
  border-radius: 20px; padding: 4px 14px;
  font-size: 0.81rem; font-weight: 500;
  white-space: nowrap; transition: all .2s;
}
.ds-step-done   { background: var(--success-bg); color: #065f46; }
.ds-step-active { background: var(--primary); color: #fff; font-weight: 700;
                  box-shadow: 0 0 0 3px var(--primary-ring); }
.ds-step-locked   { background: transparent; color: #9ca3af; }
.ds-step-optional { background: transparent; color: #9ca3af; border-style: dashed !important; }
.ds-step-arrow  { color: #d1d5db; font-size: 0.9rem; padding: 0 2px; }

/* ── Done bar (etapa concluída) ─────────────────────────────── */
.ds-done-bar {
  background: var(--success-bg);
  border: 1px solid var(--success-border);
  border-radius: var(--radius);
  padding: 10px 16px;
  margin-bottom: 4px;
}
.ds-done-label { font-size: 0.87rem; color: #065f46; }

/* ── Título de seção ────────────────────────────────────────── */
.ds-section-title {
  font-size: 1.1rem; font-weight: 700;
  color: var(--fg); margin: 0 0 3px;
}
.ds-section-caption {
  font-size: 0.82rem; color: var(--muted); margin: 0 0 16px;
}

/* ── Label de grupo ─────────────────────────────────────────── */
.ds-group-label {
  font-size: 0.71rem; font-weight: 700;
  color: var(--muted); text-transform: uppercase;
  letter-spacing: .07em; margin: 18px 0 8px;
}

/* ── Card de desfecho ───────────────────────────────────────── */
.ds-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px; min-height: 108px;
  transition: box-shadow .15s, border-color .15s;
  box-shadow: var(--shadow-sm); margin-bottom: 8px;
}
.ds-card:hover { box-shadow: var(--shadow-md); border-color: #93c5fd; }
.ds-card.selected {
  border: 2px solid var(--primary);
  background: var(--primary-light);
}
.ds-card-title { font-weight: 600; font-size: 0.88rem; color: var(--fg); margin-bottom: 5px; }
.ds-card-desc  { font-size: 0.76rem; color: var(--muted); line-height: 1.45; margin-bottom: 7px; }
.ds-card-meta  { font-size: 0.72rem; color: #9ca3af; }

/* ── Divisor ────────────────────────────────────────────────── */
.ds-divider { border: none; border-top: 1px solid var(--border); margin: 18px 0; }

/* ── Métricas ───────────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 14px 18px !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stMetricLabel"] {
  font-size: 0.76rem !important; color: var(--muted) !important; font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
  font-size: 1.45rem !important; font-weight: 700 !important; color: var(--fg) !important;
}

/* ── Botões minimalistas ─────────────────────────────────────── */
.stButton > button {
  border-radius: var(--radius) !important;
  font-size: 0.85rem !important;
  font-weight: 500 !important;
  transition: all .15s !important;
  cursor: pointer !important;
  letter-spacing: .01em !important;
}
/* Primário — azul sólido */
.stButton > button[kind="primary"] {
  background: var(--primary) !important;
  border: 1px solid var(--primary) !important;
  color: #fff !important;
  font-weight: 600 !important;
  box-shadow: none !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--primary-hover) !important;
  border-color: var(--primary-hover) !important;
  color: #fff !important;
  box-shadow: 0 0 0 3px var(--primary-ring) !important;
}
.stButton > button[kind="primary"]:focus,
.stButton > button[kind="primary"]:active {
  background: var(--primary-hover) !important;
  border-color: var(--primary-hover) !important;
  color: #fff !important;
  box-shadow: 0 0 0 3px var(--primary-ring) !important;
}
/* Secundário — outline limpo */
.stButton > button[kind="secondary"] {
  background: transparent !important;
  border: 1px solid var(--border) !important;
  color: var(--muted) !important;
  box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: var(--primary) !important;
  color: var(--primary) !important;
  background: var(--primary-light) !important;
  box-shadow: none !important;
}
.stButton > button[kind="secondary"]:focus,
.stButton > button[kind="secondary"]:active {
  border-color: var(--primary) !important;
  color: var(--primary) !important;
  background: var(--primary-light) !important;
  box-shadow: none !important;
}

/* ── Inputs — fundo branco, sem sombra interna ───────────────── */
[data-baseweb="input"],
[data-baseweb="select"] > div,
[data-baseweb="base-input"] {
  background: var(--bg) !important;
  border-color: var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow: none !important;
}
[data-testid="stMultiSelect"] > div > div,
[data-testid="stSelectbox"] > div > div {
  background: var(--bg) !important;
  border-color: var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow: none !important;
}
/* Tags do multiselect — azul primário, sem fundo escuro */
[data-baseweb="tag"] {
  background: var(--primary) !important;
  border: none !important;
  border-radius: 4px !important;
  padding: 0 8px !important;
}
[data-baseweb="tag"] span { color: #fff !important; font-size: 0.8rem !important; }
[data-baseweb="tag"] [role="button"] svg { fill: rgba(255,255,255,.8) !important; }

/* ── Labels ─────────────────────────────────────────────────── */
[data-testid="stMultiSelect"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label,
[data-testid="stCheckbox"] label,
[data-testid="stFileUploader"] label {
  color: var(--fg) !important;
  font-size: 0.84rem !important;
  font-weight: 500 !important;
}

/* ── Banners ────────────────────────────────────────────────── */
[data-testid="stInfo"],
[data-testid="stWarning"],
[data-testid="stSuccess"] { border-radius: var(--radius) !important; }

/* ── Expander ───────────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ── Dataframe ──────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: var(--radius) !important; overflow: hidden; }

/* ── Spinner ────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div { border-color: var(--primary) !important; }

/* ── Utilitário ─────────────────────────────────────────────── */
.ds-page { display: contents; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
ss = st.session_state
_defaults: dict = {
    "outcome_key": None,
    "raw_data": {},
    "cohort": None,
    "model_results": None,
    "calib_results": None,
    "comparison_results": [],
    "sel_states": ["SP"],
    "sel_years": [2023],
    "manual_needed": [],
    "sample_n": 50_000,
    "sample_seed": 42,
    "use_sample": True,
}
for k, v in _defaults.items():
    if k not in ss:
        ss[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────────
def current_step() -> int:
    if ss.get("comparison_results"):
        return 7
    if ss.get("calib_results"):
        return 6
    if ss["model_results"]:
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
        '<div class="ds-topbar-logo">'
        'DataSUS AI'
        '<span class="ds-topbar-badge">PREDICTION</span>'
        '</div>'
        '<div class="ds-topbar-right">Modelagem preditiva em saúde pública</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_step_bar(step: int) -> None:
    labels = ["Desfecho", "Dados", "Coorte", "Modelo", "Resultados", "Benchmark", "Comparação"]
    parts = []
    for i, lbl in enumerate(labels):
        n = i + 1
        optional = n >= 6
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
    col1, col2 = st.columns([13, 1])
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
        ["outcome_key", "raw_data", "cohort", "model_results", "manual_needed"],
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
                    use_container_width=True,
                    type="primary" if is_sel else "secondary",
                ):
                    for k in ["raw_data", "cohort", "model_results", "manual_needed"]:
                        ss[k] = _defaults[k]
                    ss["outcome_key"] = key
                    st.rerun()
    st.stop()

st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)
outcome = OUTCOMES[ss["outcome_key"]]

# ── Lazy: módulos de dados e visualização (step 2+) ──────────────────────────
pd = _pd()
px = _px()
STATES, ManualUploadRequired, fetch, load_from_csv = _dl()

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 2 — DADOS
# ═════════════════════════════════════════════════════════════════════════════
if ss["raw_data"]:
    summary = " &nbsp;·&nbsp; ".join(
        f"{src}: <strong>{len(df):,}</strong>" for src, df in ss["raw_data"].items()
    )
    done_bar(summary, "chg_data",
             ["raw_data", "cohort", "model_results", "manual_needed"])
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
        _download_clicked = st.button("Baixar", type="primary", use_container_width=True)

    # ── Linha 2: Configuração de Amostragem ────────────────────────────────────
    st.markdown("<div style='margin-top:.75rem'></div>", unsafe_allow_html=True)
    with st.expander("⚙️ Configuração de Amostragem", expanded=True):
        sa1, sa2, sa3 = st.columns([1, 1, 2])
        with sa1:
            ss["use_sample"] = st.toggle(
                "Usar amostragem",
                value=ss["use_sample"],
                help="Se ativado, limita o dataset ao número de registros abaixo. "
                     "Recomendado para testes rápidos.",
            )
        with sa2:
            ss["sample_n"] = st.number_input(
                "Tamanho da amostra",
                min_value=1_000,
                max_value=500_000,
                value=ss["sample_n"],
                step=5_000,
                disabled=not ss["use_sample"],
                help="Número máximo de registros a usar após o download.",
            )
        with sa3:
            ss["sample_seed"] = st.number_input(
                "Seed (reprodutibilidade)",
                min_value=0,
                max_value=99_999,
                value=ss["sample_seed"],
                step=1,
                disabled=not ss["use_sample"],
                help="Seed aleatória fixa para garantir resultados reproduzíveis.",
            )
        if ss["use_sample"]:
            st.caption(
                f"Serão usados até **{ss['sample_n']:,}** registros "
                f"amostrados aleatoriamente com seed **{ss['sample_seed']}**. "
                "Desative para usar o dataset completo."
            )
        else:
            st.caption("Dataset completo será usado — pode ser lento para grandes estados/anos.")

    if _download_clicked:
        raw_data: dict = {}
        manual_needed: list = []
        for source in outcome.data_sources:
            prog = st.progress(0.0, text=f"Baixando {source}…")
            try:
                dfs = []
                for state in ss["sel_states"]:
                    for year in ss["sel_years"]:
                        dfs.append(
                            fetch(source, state, year,
                                  lambda p, m, _p=prog: _p.progress(min(p, 1.0), text=m))
                        )
                df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

                # ── Amostragem ─────────────────────────────────────────────────
                if ss["use_sample"] and len(df) > ss["sample_n"]:
                    df = df.sample(n=ss["sample_n"], random_state=ss["sample_seed"]).reset_index(drop=True)
                    prog.progress(1.0, text=f"{source}: {len(df):,} registros (amostra)")
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

# ── Lazy: CohortBuilder (só carrega ao chegar na etapa 3) ────────────────────
CohortBuilder = _cohort()

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 3 — COORTE
# ═════════════════════════════════════════════════════════════════════════════
if ss["cohort"] is not None:
    cohort = ss["cohort"]
    builder = CohortBuilder(outcome)
    bal = builder.class_balance(cohort)
    done_bar(
        f'<strong>{bal["total"]:,}</strong> registros &nbsp;·&nbsp; '
        f'prevalência <strong>{bal["prevalence"]:.1%}</strong>',
        "chg_cohort",
        ["cohort", "model_results"],
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", f"{bal['total']:,}")
    c2.metric("Positivos", f"{bal['positive']:,}")
    c3.metric("Negativos", f"{bal['negative']:,}")
    c4.metric("Prevalência", f"{bal['prevalence']:.1%}")

    with st.expander("Distribuição e dados faltantes"):
        ca, cb = st.columns(2)
        with ca:
            fig_pie = px.pie(
                values=[bal["positive"], bal["negative"]],
                names=["Positivo (1)", "Negativo (0)"],
                color_discrete_sequence=["#ef4444", "#3b82f6"],
                title="Distribuição do desfecho",
            )
            fig_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=260)
            st.plotly_chart(fig_pie, use_container_width=True)
        with cb:
            missing = (cohort.isnull().mean() * 100).sort_values(ascending=False)
            missing = missing[missing > 0].head(15)
            if not missing.empty:
                fig_miss = px.bar(
                    x=missing.values, y=missing.index, orientation="h",
                    labels={"x": "% faltante", "y": ""},
                    title="Dados faltantes por coluna",
                    color=missing.values, color_continuous_scale="Reds",
                )
                fig_miss.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=260, showlegend=False)
                st.plotly_chart(fig_miss, use_container_width=True)
            else:
                st.success("Sem dados faltantes.")
        st.dataframe(cohort.head(50), use_container_width=True)
else:
    step_title(3, "Construir Coorte",
               "Filtra casos elegíveis, cria features e define o target para o modelo.")
    if st.button("Construir Coorte", type="primary", use_container_width=True):
        with st.spinner("Construindo coorte…"):
            try:
                builder = CohortBuilder(outcome)
                ss["cohort"] = builder.build(ss["raw_data"])
                ss["model_results"] = None
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao construir coorte: {e}")
                st.exception(e)
    st.stop()

st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── Lazy: pipeline ML (só carrega ao chegar na etapa 4) ──────────────────────
ALGORITHMS, train_cv, optimize_hyperparams, calibrate_model = _pipeline()

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 4 — MODELO
# ═════════════════════════════════════════════════════════════════════════════
cohort = ss["cohort"]
builder = CohortBuilder(outcome)
X, y = builder.get_Xy(cohort)

if ss["model_results"]:
    results = ss["model_results"]
    m = results["mean_metrics"]
    sample_info = ""
    total_n_done = bal["total"] if "bal" in dir() else results.get("sample_n", "?")
    if results.get("sample_n") and results["sample_n"] < len(cohort):
        sample_info = f' &nbsp;·&nbsp; amostra <strong>{results["sample_n"]:,}</strong>'
    hpo_tag = " · Optuna" if results.get("hpo_mode") == "Optuna (automático)" else ""
    done_bar(
        f'<strong>{results["algorithm"].upper()}</strong>{hpo_tag} &nbsp;·&nbsp; '
        f'AUC <strong>{m["roc_auc"]:.3f}</strong> &nbsp;·&nbsp; '
        f'F1 <strong>{m["f1"]:.3f}</strong> &nbsp;·&nbsp; '
        f'PR-AUC <strong>{m["pr_auc"]:.3f}</strong>{sample_info}',
        "chg_model",
        ["model_results", "calib_results", "comparison_results"],
    )
else:
    step_title(4, "Treinar Modelo",
               "Configure o algoritmo, amostragem e hiperparâmetros. Validação cruzada estratificada.")
    bal = builder.class_balance(cohort)
    total_n = bal["total"]
    st.info(
        f"**{total_n:,}** registros · prevalência **{bal['prevalence']:.1%}** · "
        f"**{len(X.columns)}** features disponíveis"
    )

    # ── Amostragem ────────────────────────────────────────────────────────────
    st.markdown("**Amostragem**")
    use_sample = st.checkbox(
        "Usar amostra para treinamento",
        value=False,
        help="Útil para exploração rápida em coortes grandes. A amostra é estratificada pelo desfecho.",
    )
    if use_sample:
        max_sample = min(total_n, 50_000)
        default_sample = min(total_n, 5_000)
        sample_n = st.slider(
            "Tamanho da amostra", 500, max_sample, default_sample, 500,
            help="Número de registros selecionados de forma estratificada para treino.",
        )
    else:
        sample_n = total_n

    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

    # ── Algoritmo e validação ─────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Algoritmo e validação**")
        algo_label = st.selectbox("Algoritmo", list(ALGORITHMS.keys()))
        algo = ALGORITHMS[algo_label]
        n_folds = st.slider("Folds (cross-validation)", 3, 10, 5)
        use_smote = st.checkbox(
            "SMOTE — oversample da classe minoritária",
            help="Recomendado quando prevalência < 5%",
        )
        st.markdown("**Modo de hiperparâmetros**")
        hpo_mode = st.radio(
            "Modo",
            ["Manual", "Optuna (automático)"],
            horizontal=True,
            label_visibility="collapsed",
            help="Optuna busca automaticamente os melhores hiperparâmetros via otimização bayesiana.",
        )
        if hpo_mode == "Optuna (automático)":
            n_trials = st.slider(
                "Tentativas (trials)", 10, 200, 50, 10,
                help="Mais tentativas = maior chance de encontrar bons parâmetros, mas mais lento.",
            )

    with c2:
        if hpo_mode == "Manual":
            st.markdown("**Hiperparâmetros**")
            params: dict = {}
            if algo in ("lgbm", "xgb", "rf"):
                params["n_estimators"] = st.slider("Árvores (n_estimators)", 50, 1000, 300, 50)
            if algo in ("lgbm", "xgb"):
                params["learning_rate"] = st.select_slider(
                    "Learning rate", [0.005, 0.01, 0.02, 0.05, 0.1, 0.2], value=0.05
                )
            if algo in ("lgbm", "xgb", "rf"):
                params["max_depth"] = st.slider("max_depth (−1 = sem limite)", -1, 15, -1)
            if algo == "logreg":
                params["C"] = st.select_slider(
                    "C (regularização)", [0.001, 0.01, 0.1, 1.0, 10.0], value=1.0
                )
        else:
            params = {}
            st.markdown("**Optuna**")
            st.caption(
                "Os hiperparâmetros serão buscados automaticamente por otimização bayesiana "
                f"em {n_trials} tentativas com {min(n_folds, 3)}-fold CV interno. "
                "Os melhores parâmetros encontrados ficam visíveis nos resultados."
            )

    # ── Features ──────────────────────────────────────────────────────────────
    selected_features = st.multiselect(
        "Features para o modelo", X.columns.tolist(), default=X.columns.tolist(),
        help="Por padrão todas as features sugeridas são incluídas.",
    )
    if not selected_features:
        st.warning("Selecione pelo menos uma feature.")
        st.stop()

    btn_label = (
        f"Otimizar + Treinar {algo_label} com {n_folds}-fold CV"
        if hpo_mode == "Optuna (automático)"
        else f"Treinar {algo_label} com {n_folds}-fold CV"
    )
    if use_sample and sample_n < total_n:
        btn_label += f" (amostra {sample_n:,})"

    if st.button(btn_label, type="primary", use_container_width=True):
        try:
            from sklearn.model_selection import train_test_split

            X_train = X[selected_features]
            y_train = y

            # Aplica amostragem estratificada se necessário
            if use_sample and sample_n < total_n:
                X_train, _, y_train, _ = train_test_split(
                    X_train, y_train,
                    train_size=sample_n,
                    stratify=y_train,
                    random_state=42,
                )

            # Otimização Optuna (se selecionada)
            if hpo_mode == "Optuna (automático)":
                prog = st.progress(0.0, text="Iniciando Optuna…")

                def _optuna_cb(done, total, best):
                    pct = done / total
                    prog.progress(pct, text=f"Optuna: trial {done}/{total} — melhor ROC-AUC {best:.4f}")

                params = optimize_hyperparams(
                    X_train, y_train,
                    algorithm=algo,
                    n_trials=n_trials,
                    n_folds=min(n_folds, 3),
                    use_smote=use_smote,
                    progress_callback=_optuna_cb,
                )
                prog.progress(1.0, text=f"Optuna concluído — {n_trials} trials")

            with st.spinner(f"Treinando {algo_label} com {n_folds}-fold CV…"):
                results = train_cv(
                    X=X_train, y=y_train, algorithm=algo,
                    params=params, n_folds=n_folds, use_smote=use_smote,
                )
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

# ── Lazy: evaluation (só carrega ao chegar na etapa 5) ───────────────────────
ev = _ev()

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 5 — RESULTADOS
# ═════════════════════════════════════════════════════════════════════════════
results = ss["model_results"]
st.markdown(
    '<p class="ds-section-title">Resultados do Modelo</p>'
    '<p class="ds-section-caption">Métricas de desempenho, curvas ROC/PR, explicabilidade SHAP e exportação.</p>',
    unsafe_allow_html=True,
)

m = results["mean_metrics"]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("ROC-AUC", f"{m['roc_auc']:.4f}")
c2.metric("PR-AUC", f"{m['pr_auc']:.4f}")
c3.metric("F1-Score", f"{m['f1']:.4f}")
c4.metric("Recall", f"{m['recall']:.4f}")
c5.metric("Brier Score", f"{m['brier']:.4f}")

col_exp1, col_exp2 = st.columns(2)
with col_exp1:
    with st.expander("Métricas por fold"):
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

st.markdown("#### SHAP — Explicabilidade")
with st.spinner("Calculando SHAP…"):
    shap_fig = ev.shap_summary(results["model"], X_res.head(500))
if shap_fig:
    st.plotly_chart(shap_fig, use_container_width=False)
else:
    st.info("SHAP indisponível para este algoritmo. Instale: `pip install shap`")

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


# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 6 — BENCHMARK (opcional)
# ═════════════════════════════════════════════════════════════════════════════
step_title(6, "Benchmark do Modelo",
           "Ajusta as probabilidades para que reflitam frequências reais. Opcional — pule se não necessário.")

if ss["calib_results"]:
    cr = ss["calib_results"]
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
            st.success("Benchmark melhorou as probabilidades.")
        elif delta < 0:
            st.warning("Benchmark piorou levemente. Considere o método alternativo.")
        else:
            st.info("Sem variação significativa.")
else:
    c_col1, c_col2 = st.columns([2, 1])
    with c_col1:
        calib_method = st.radio(
            "Método de benchmark",
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
            "O benchmark usa 25% dos dados como holdout interno para ajustar "
            "as probabilidades sem vazar informação do treino."
        )
    col_cb1, col_cb2 = st.columns(2)
    with col_cb1:
        if st.button("Executar Benchmark", type="primary", use_container_width=True):
            with st.spinner("Executando benchmark…"):
                try:
                    cr = calibrate_model(
                        results["model"],
                        X_res,
                        y,
                        method=calib_method,
                    )
                    ss["calib_results"] = cr
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro no benchmark: {e}")
    with col_cb2:
        if st.button("Pular benchmark", type="secondary", use_container_width=True):
            ss["calib_results"] = {"skipped": True, "cal_model": results["model"]}
            st.rerun()

st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 7 — COMPARAÇÃO ENTRE ESTADOS (opcional)
# ═════════════════════════════════════════════════════════════════════════════
step_title(7, "Comparação entre Estados",
           "Aplica o modelo treinado a novas coortes de outros estados e compara métricas e explicabilidade SHAP.")

# Modelo a usar: calibrado (se disponível e não pulado) ou original
_active_model = results["model"]
if ss.get("calib_results") and not ss["calib_results"].get("skipped"):
    _active_model = ss["calib_results"]["cal_model"]

if ss["comparison_results"]:
    comp = ss["comparison_results"]
    st.markdown("**Métricas por coorte**")
    st.dataframe(
        ev.metrics_comparison_table(comp),
        use_container_width=True,
        hide_index=True,
    )

    shap_dicts = [r["shap_dict"] for r in comp if r.get("shap_dict")]
    shap_labels = [r["label"] for r in comp if r.get("shap_dict")]
    if len(shap_dicts) >= 2:
        st.markdown("**Comparação SHAP entre coortes**")
        st.plotly_chart(
            ev.shap_comparison_chart(shap_dicts, shap_labels),
            use_container_width=True,
        )

    if st.button("Limpar e comparar outros estados", type="secondary"):
        ss["comparison_results"] = []
        st.rerun()
else:
    st.info(
        "Selecione estados adicionais para comparar o desempenho do mesmo modelo "
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
            f"Incluir coorte original ({', '.join(already_used)})",
            value=True,
        )
    with cmp_col2:
        cmp_years = st.multiselect(
            "Anos",
            list(range(2018, 2025)),
            default=ss["sel_years"],
        )

    if not cmp_states and not include_original:
        st.warning("Selecione pelo menos um estado ou mantenha a coorte original.")
    elif st.button("Rodar comparação", type="primary", use_container_width=True):
        comp_list = []

        # Helper: run a single state group
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

                # Align columns to trained model
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

                return {
                    "label": label,
                    "n": len(y_cmp),
                    "metrics": metrics_cmp,
                    "shap_dict": shap_d,
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
                (f"{st_} · {'+'.join(map(str, cmp_years))}",
                 [st_], cmp_years, None)
            )

        for idx, (lbl, sts, yrs, raw_ov) in enumerate(all_groups):
            prog_cmp.progress((idx) / len(all_groups), text=f"Processando {lbl}…")
            r = _run_state_group(lbl, sts, yrs, raw_ov)
            if r:
                comp_list.append(r)

        prog_cmp.progress(1.0, text="Comparação concluída.")
        ss["comparison_results"] = comp_list
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)  # fecha ds-page
