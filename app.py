"""DataSUS AI Prediction — home page minima, zero imports pesados."""
from pathlib import Path
from PIL import Image as _PILImage
import streamlit as st

_favicon = _PILImage.open(Path(__file__).parent / "favicon.png")
st.set_page_config(
    page_title="DataSUS AI Prediction",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Metadados dos desfechos — ícone = nome Material Symbol ───────────────────

OUTCOME_GROUPS = {
    "Internacao Hospitalar": [
        ("readmissao_30d",           "sync",                "Readmissao Hospitalar 30 dias",          "SIH"),
        ("mortalidade_hospitalar",   "monitor_heart",       "Mortalidade Hospitalar",                  "SIH + SIM"),
        ("permanencia_prolongada",   "bed",                 "Permanencia Prolongada",                  "SIH"),
        ("infeccao_hospitalar",      "coronavirus",         "Infeccao Hospitalar",                     "SIH"),
        ("custo_elevado",            "payments",            "Custo Hospitalar Elevado",                "SIH"),
    ],
    "Saude Materno-Infantil": [
        ("mortalidade_neonatal",     "child_care",          "Mortalidade Neonatal",                    "SINASC + SIM"),
        ("baixo_peso_nascer",        "scale",               "Baixo Peso ao Nascer",                    "SINASC"),
        ("prematuridade",            "baby_changing_station","Prematuridade",                          "SINASC"),
        ("apgar_baixo",              "cardiology",          "Apgar Baixo no 5 Minuto",                "SINASC"),
    ],
    "SINAN — Agravos e Doencas de Notificacao": [
        ("abandono_tb",              "pulmonology",         "Abandono de Tratamento TB",               "SINAN"),
        ("abandono_hanseniase",      "stethoscope",         "Abandono de Tratamento Hanseniase",       "SINAN"),
        ("dengue_grave",             "pest_control",        "Dengue Grave ou com Sinais de Alarme",    "SINAN"),
        ("chikungunya_hospitalizado","local_hospital",      "Hospitalizacao por Chikungunya",          "SINAN"),
        ("obito_aids",               "medical_information", "Obito por AIDS",                          "SINAN"),
        ("sifilis_nao_cura",         "medication",          "Nao-Cura de Sifilis Adquirida",           "SINAN"),
        ("violencia_autoprovocada",  "psychology",          "Risco de Violencia Autoprovocada",        "SINAN"),
        ("intoxicacao_grave",        "warning",             "Desfecho Adverso em Intoxicacao Exogena", "SINAN"),
    ],
}

# ── Session state ─────────────────────────────────────────────────────────────
if "outcome_key" not in st.session_state:
    st.session_state.outcome_key = None

# ── CSS + Material Symbols ────────────────────────────────────────────────────
st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,300,0,0" />

<style>
header, footer,
[data-testid="stSidebar"], [data-testid="stSidebarNav"],
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], #MainMenu { display: none !important; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {
    background-color: #ffffff !important;
    color: #111827 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif !important;
}

.block-container {
    padding: 3rem 3rem !important;
    max-width: 1100px !important;
}

.ms {
    font-family: 'Material Symbols Outlined';
    font-style: normal; font-weight: normal;
    font-size: 1rem; line-height: 1;
    vertical-align: middle; display: inline-block;
    color: #111827;
}
.ms-lg { font-size: 1.4rem; margin-right: .25rem; }

.ds-title {
    font-size: 1.6rem; font-weight: 700;
    color: #111827 !important; margin-bottom: .15rem;
    display: flex; align-items: center; gap: .35rem;
}
.ds-sub {
    font-size: 0.9rem; color: #6b7280 !important; margin-bottom: 2.5rem;
}
.ds-group {
    font-size: .68rem; font-weight: 700;
    color: #9ca3af !important; text-transform: uppercase;
    letter-spacing: .1em; margin: 1.75rem 0 .5rem;
    padding-bottom: .35rem; border-bottom: 1px solid #f3f4f6;
}

/* Cards */
.ds-card {
    border: 1px solid #e5e7eb; border-radius: 6px;
    padding: .75rem 1rem; margin-bottom: .5rem;
    background: #ffffff !important; height: 96px;
    display: flex; flex-direction: column;
    justify-content: space-between; overflow: hidden;
    transition: border-color .12s;
}
.ds-card:hover { border-color: #9ca3af; }
.ds-card strong {
    font-size: .81rem; color: #111827 !important;
    display: flex; align-items: flex-start;
    gap: .3rem; line-height: 1.3; flex: 1;
}
.ds-card strong .ms { flex-shrink: 0; margin-top: .05rem; }
.ds-card.sel { border: 1.5px solid #111827; background: #f9fafb !important; }
.ds-badge {
    font-size: .66rem; color: #9ca3af !important;
    font-weight: 500; margin-top: .2rem;
}

/* Botoes */
div[data-testid="stButton"] {
    display: flex !important; justify-content: flex-start !important;
}
div[data-testid="stButton"] > button {
    background-color: #ffffff !important; color: #111827 !important;
    border: 1px solid #e5e7eb !important; border-radius: 6px !important;
    font-size: .8rem !important; font-weight: 500 !important;
    padding: 5px 16px !important; width: auto !important;
    transition: all .12s !important;
}
div[data-testid="stButton"] > button:hover {
    background-color: #f3f4f6 !important;
    border-color: #111827 !important;
}
div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
    background-color: #111827 !important; color: #ffffff !important;
    border-color: #111827 !important; font-weight: 600 !important;
}
div[data-testid="stButton"] > button[data-testid="baseButton-primary"]:hover {
    background-color: #374151 !important; border-color: #374151 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<p class="ds-title">'
    '<span class="ms ms-lg">local_hospital</span>'
    'DataSUS AI Prediction'
    '</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="ds-sub">Modelagem preditiva em saude publica — selecione o desfecho para comecar</p>',
    unsafe_allow_html=True,
)

# ── Selecao de desfecho ───────────────────────────────────────────────────────
try:
    sel = st.session_state.outcome_key

    N_COLS = 5
    for group_name, outcomes in OUTCOME_GROUPS.items():
        st.markdown(f'<p class="ds-group">{group_name}</p>', unsafe_allow_html=True)
        for row_start in range(0, len(outcomes), N_COLS):
            row = outcomes[row_start : row_start + N_COLS]
            cols = st.columns(N_COLS)
            for col_idx, (key, icon, name, source) in enumerate(row):
                with cols[col_idx]:
                    is_sel = sel == key
                    cls = "ds-card sel" if is_sel else "ds-card"
                    st.markdown(
                        f'<div class="{cls}">'
                        f'<strong><span class="ms">{icon}</span>{name}</strong>'
                        f'<span class="ds-badge">{source}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    try:
                        clicked = st.button(
                            "Selecionar", key=f"sel_{key}",
                            type="primary" if is_sel else "secondary",
                            use_container_width=True,
                        )
                    except TypeError:
                        clicked = st.button(
                            "Selecionar", key=f"sel_{key}",
                            type="primary" if is_sel else "secondary",
                        )
                    if clicked:
                        st.session_state.outcome_key = key
                        st.switch_page("pages/analise.py")

except Exception as e:
    import traceback
    st.error(f"**Erro na aplicacao:** {e}")
    st.code(traceback.format_exc())
