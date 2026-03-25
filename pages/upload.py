"""DataSUS AI Prediction — Upload & DIY: carrega base própria e entra no pipeline normal."""
from __future__ import annotations
import json as _json
from pathlib import Path
from PIL import Image as _PILImage

import streamlit as st
import streamlit.components.v1 as _stc
from core.outcomes import OUTCOMES

# ── Page config ───────────────────────────────────────────────────────────────
_favicon = _PILImage.open(Path(__file__).parent.parent / "favicon.png")
st.set_page_config(
    page_title="Upload — DataSUS AI Prediction",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS via JavaScript (bypasses Streamlit's markdown parser) ─────────────────
_CSS = (
    "header,footer,[data-testid='stSidebarNav'],[data-testid='stHeader'],"
    "[data-testid='stToolbar'],[data-testid='stDecoration'],#MainMenu{display:none!important}"
    "html,body,.stApp,[data-testid='stAppViewContainer'],[data-testid='stMain'],.main,.block-container{"
    "background:#ffffff!important;font-family:-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',sans-serif!important;"
    "color:#111827!important}"
    ".block-container{padding:2.5rem 3rem!important;max-width:1100px!important}"
    ".ms{font-family:'Material Symbols Outlined';font-style:normal;font-weight:normal;"
    "font-size:1rem;line-height:1;vertical-align:middle;display:inline-block;color:#111827}"
    ".ms-lg{font-size:1.4rem;margin-right:.25rem}"
    ".up-title{font-size:1.3rem;font-weight:700;color:#111827!important;"
    "display:flex;align-items:center;gap:.35rem;margin-bottom:.1rem}"
    ".up-sub{font-size:.85rem;color:#6b7280!important;margin-bottom:1.25rem}"
    ".up-step{font-size:.66rem;font-weight:700;color:#9ca3af!important;text-transform:uppercase;"
    "letter-spacing:.1em;margin:1.4rem 0 .4rem;padding-bottom:.28rem;border-bottom:1px solid #f3f4f6}"
    ".up-info{background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;"
    "padding:.55rem .85rem;font-size:.8rem;color:#374151;margin-bottom:.65rem;line-height:1.5}"
    "div[data-testid='stButton']>button[data-testid='baseButton-primary']{"
    "background-color:#111827!important;color:#ffffff!important;border:1px solid #111827!important;"
    "border-radius:6px!important;font-size:.82rem!important;font-weight:600!important}"
    "div[data-testid='stButton']>button[data-testid='baseButton-primary']:hover{"
    "background-color:#374151!important;border-color:#374151!important}"
    "div[data-testid='stButton']>button{border-radius:6px!important;font-size:.82rem!important}"
)

_stc.html(
    "<script>"
    "(function(){"
    "var l=document.createElement('link');"
    "l.rel='stylesheet';"
    "l.href='https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,300,0,0';"
    "window.parent.document.head.appendChild(l);"
    "var s=document.createElement('style');"
    f"s.textContent={_json.dumps(_CSS)};"
    "window.parent.document.head.appendChild(s);"
    "})();"
    "</script>",
    height=0,
    scrolling=False,
)

import pandas as pd
import numpy as np
from core.data.downloader import STATES, load_from_csv

ss = st.session_state

# ── Identify mode ─────────────────────────────────────────────────────────────
outcome_key = ss.get("outcome_key")
is_diy = (outcome_key == "__diy__")
outcome = None if is_diy else OUTCOMES.get(outcome_key)

# ── Header ────────────────────────────────────────────────────────────────────
_back_col, _ = st.columns([1, 9])
with _back_col:
    if st.button("← Voltar", key="up_back"):
        if is_diy:
            ss["outcome_key"] = None
        st.switch_page("app.py")

if is_diy:
    st.markdown(
        '<p class="up-title"><span class="ms ms-lg">construction</span>Do It Yourself (DIY)</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="up-sub">Carregue qualquer base de saúde em CSV ou Parquet, '
        'defina o desfecho e rode o pipeline completo.</p>',
        unsafe_allow_html=True,
    )
else:
    _src = ", ".join(outcome.data_sources) if outcome else ""
    st.markdown(
        f'<p class="up-title">'
        f'<span class="ms ms-lg">upload_file</span>Upload — {outcome.name if outcome else ""}'
        f'</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="up-sub">Carregue o arquivo da base <b>{_src}</b> para continuar o pipeline.</p>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — ARQUIVO
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="up-step">1. Carregar arquivo</p>', unsafe_allow_html=True)

if is_diy:
    st.markdown(
        '<div class="up-info">'
        '<b>Formatos:</b> CSV (vírgula ou ponto-e-vírgula) e Parquet. '
        'A primeira linha deve conter os nomes das colunas.'
        '</div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Selecione o arquivo", type=["csv", "parquet"],
        key="up_file_diy", label_visibility="collapsed",
    )
else:
    _sources = outcome.data_sources if outcome else []
    st.markdown(
        '<div class="up-info">'
        f'<b>Formato esperado:</b> arquivo DBC ou CSV exportado do DATASUS para a base '
        f'<b>{", ".join(_sources)}</b>.<br>'
        'Também aceita o CSV gerado pelo TabNet ou pelo próprio sistema de download.'
        '</div>',
        unsafe_allow_html=True,
    )

    # State / year for metadata (used in load_from_csv)
    _uc1, _uc2 = st.columns(2)
    with _uc1:
        _sel_state = st.selectbox("Estado (UF)", STATES, index=STATES.index("SP") if "SP" in STATES else 0, key="up_state")
    with _uc2:
        _sel_year = st.selectbox("Ano", list(range(2018, 2026)), index=5, key="up_year")

    uploaded_file = st.file_uploader(
        f"Arquivo {_sources[0] if _sources else ''} (CSV / DBC)",
        type=["csv", "txt", "dbc"],
        key="up_file_outcome",
        label_visibility="collapsed",
    )

if uploaded_file is None:
    st.stop()

# ── Read file ─────────────────────────────────────────────────────────────────
try:
    if is_diy:
        if uploaded_file.name.endswith(".parquet"):
            df_raw = pd.read_parquet(uploaded_file)
        else:
            try:
                df_raw = pd.read_csv(uploaded_file, sep=None, engine="python", low_memory=False)
            except Exception:
                uploaded_file.seek(0)
                df_raw = pd.read_csv(uploaded_file, sep=";", low_memory=False)
    else:
        # Use load_from_csv to apply DATASUS-specific preprocessing
        source = _sources[0] if _sources else "UPLOAD"
        df_raw = load_from_csv(uploaded_file.read(), source, _sel_state, _sel_year)
except Exception as e:
    st.error(f"Erro ao ler o arquivo: {e}")
    st.stop()

st.success(f"Arquivo carregado: **{len(df_raw):,} linhas × {len(df_raw.columns)} colunas**")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2 — REVISAR DADOS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="up-step">2. Revisar dados</p>', unsafe_allow_html=True)

_n, _k = df_raw.shape
_miss_pct = df_raw.isna().sum().sum() / max(_n * _k, 1)
_m1, _m2, _m3 = st.columns(3)
_m1.metric("Registros", f"{_n:,}")
_m2.metric("Colunas", str(_k))
_m3.metric("Completude geral", f"{1 - _miss_pct:.1%}")

with st.expander("Sumário estatístico", expanded=False):
    _num = df_raw.select_dtypes(include="number")
    _cat = df_raw.select_dtypes(exclude="number")
    if not _num.empty:
        st.markdown("**Variáveis numéricas**")
        st.dataframe(_num.describe().T.round(2), use_container_width=True)
    if not _cat.empty:
        st.markdown("**Variáveis categóricas (primeiras 5)**")
        st.dataframe(
            _cat.iloc[:, :5].describe(include="all").T,
            use_container_width=True,
        )

with st.expander("Amostra dos dados (10 linhas)", expanded=False):
    st.dataframe(df_raw.head(10), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — DESFECHO (coluna alvo)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="up-step">3. Variável desfecho (coluna alvo binária)</p>', unsafe_allow_html=True)

all_cols = list(df_raw.columns)

# Suggest default target
if is_diy:
    _binary_candidates = [
        c for c in all_cols
        if df_raw[c].dropna().nunique() == 2
        and set(df_raw[c].dropna().unique()).issubset({0, 1, "0", "1", True, False})
    ]
    _default_target_idx = all_cols.index(_binary_candidates[0]) if _binary_candidates else 0
else:
    _default_target = outcome.target_col if outcome else all_cols[0]
    _default_target_idx = all_cols.index(_default_target) if _default_target in all_cols else 0

target_col = st.selectbox(
    "Coluna alvo (0 = negativo, 1 = positivo)",
    options=all_cols,
    index=_default_target_idx,
    key="up_target",
    help="Selecione a coluna que representa o desfecho binário a predizer.",
)

# Validate binary
_tvals = df_raw[target_col].dropna().unique()
_coercible = all(str(v) in {"0", "1", "0.0", "1.0", "True", "False"} for v in _tvals)
if not _coercible and len(_tvals) > 2:
    st.warning(
        f"**{target_col}** tem {len(_tvals)} valores únicos. "
        "Selecione uma coluna com apenas 2 valores (0/1)."
    )
    st.stop()

_y_preview = df_raw[target_col].astype(str).map({"0": 0, "1": 1, "0.0": 0, "1.0": 1, "True": 1, "False": 0}).fillna(df_raw[target_col])
try:
    _y_preview = _y_preview.astype(int)
    _pos_rate = _y_preview.mean()
    _tc1, _tc2, _tc3 = st.columns(3)
    _tc1.metric("Total", f"{len(_y_preview):,}")
    _tc2.metric("Positivos (1)", f"{_y_preview.sum():,} ({_pos_rate:.1%})")
    _tc3.metric("Negativos (0)", f"{(~_y_preview.astype(bool)).sum():,} ({1-_pos_rate:.1%})")
    if _pos_rate < 0.03 or _pos_rate > 0.97:
        st.warning("Prevalência muito extrema. Considere balanceamento na etapa de configuração do modelo.")
except Exception:
    st.warning("Não foi possível validar a distribuição do desfecho.")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4 — FEATURES (apenas DIY ou se desfecho foi alterado)
# ═══════════════════════════════════════════════════════════════════════════════
show_feature_step = is_diy or (not is_diy and outcome and target_col != outcome.target_col)
feature_cols: list[str] = []

if show_feature_step or is_diy:
    st.markdown('<p class="up-step">4. Variáveis preditoras</p>', unsafe_allow_html=True)
    _feat_options = [c for c in all_cols if c != target_col]
    if is_diy:
        _feat_default = []
        _feat_help = "Deixe vazio para usar todas as colunas exceto o alvo."
    else:
        _feat_default = [c for c in (outcome.suggested_features or []) if c in _feat_options]
        _feat_help = "Features sugeridas pelo desfecho pré-selecionadas."

    feature_cols = st.multiselect(
        "Selecione as variáveis preditoras",
        options=_feat_options,
        default=_feat_default,
        key="up_features",
        help=_feat_help,
    )
    if not feature_cols:
        feature_cols = _feat_options
        st.caption(f"Usando todas as {len(feature_cols)} colunas como preditoras.")
    else:
        st.caption(f"{len(feature_cols)} variáveis selecionadas.")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5 — DICIONÁRIO DE DADOS (inputs de texto)
# ═══════════════════════════════════════════════════════════════════════════════
_dict_step_n = "5" if (show_feature_step or is_diy) else "4"
st.markdown(f'<p class="up-step">{_dict_step_n}. Dicionário de dados (opcional)</p>', unsafe_allow_html=True)
st.markdown(
    '<div class="up-info">'
    'Preencha o rótulo e a descrição de cada variável. '
    'Serão exibidos na etapa de Features do pipeline.'
    '</div>',
    unsafe_allow_html=True,
)

# Determine which cols to show in dict
_dict_cols = feature_cols if feature_cols else [c for c in all_cols if c != target_col]

# Load existing custom dict from session state
_existing_dict: dict = ss.get("upload_dict") or {}

_new_dict: dict = {}
with st.expander(f"Editar dicionário — {len(_dict_cols)} variáveis", expanded=False):
    for _dc in _dict_cols:
        _existing = _existing_dict.get(_dc, {})
        _col_a, _col_b, _col_c = st.columns([2, 3, 1])
        with _col_a:
            st.markdown(f"<div style='padding-top:6px;font-weight:600;font-size:.82rem'>{_dc}</div>", unsafe_allow_html=True)
        with _col_b:
            _lbl = st.text_input(
                "Rótulo", value=_existing.get("label", ""), key=f"dict_lbl_{_dc}",
                placeholder="Ex: Idade do paciente", label_visibility="collapsed",
            )
        with _col_c:
            _typ = st.selectbox(
                "Tipo", ["", "Numérica", "Categórica", "Ordinal", "Derivada"],
                index=["", "Numérica", "Categórica", "Ordinal", "Derivada"].index(_existing.get("type", "")) if _existing.get("type", "") in ["", "Numérica", "Categórica", "Ordinal", "Derivada"] else 0,
                key=f"dict_typ_{_dc}",
                label_visibility="collapsed",
            )
        _desc = st.text_input(
            "Descrição", value=_existing.get("desc", ""), key=f"dict_desc_{_dc}",
            placeholder="Breve descrição da variável...",
            label_visibility="collapsed",
        )
        if _lbl or _desc:
            _new_dict[_dc] = {"label": _lbl or _dc, "desc": _desc, "type": _typ}
        st.markdown("<div style='height:2px;border-top:1px solid #f3f4f6;margin:4px 0'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CONTINUAR
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

if st.button("Continuar para o Pipeline →", type="primary", key="up_continue"):
    # Reset pipeline state
    for _k in ["cohort", "feature_config", "treatment_config", "model_config",
               "model_results", "calib_results", "comparison_results", "model_results",
               "X_res", "manual_needed"]:
        ss[_k] = None if _k not in ("comparison_results", "manual_needed") else []

    # Store custom dict
    ss["upload_dict"] = _new_dict

    if is_diy:
        # DIY: store df and metadata for analise.py to use
        ss["upload_df"] = df_raw
        ss["upload_target"] = target_col
        ss["upload_features"] = feature_cols
        ss["raw_data"] = {}
    else:
        # Upload outcome: store as raw_data so analise.py proceeds normally
        source = _sources[0] if _sources else "UPLOAD"
        ss["raw_data"] = {source: df_raw}
        ss["upload_df"] = None
        ss["upload_target"] = target_col  # may differ from outcome.target_col
        ss["upload_features"] = feature_cols

    st.switch_page("pages/analise.py")
