"""DataSUS AI Prediction — home page minima, zero imports pesados."""
import streamlit as st

st.set_page_config(
    page_title="DataSUS AI Prediction",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Metadados dos desfechos (hardcoded — zero imports) ────────────────────────

OUTCOME_GROUPS = {
    "Internacao Hospitalar": [
        ("readmissao_30d",        "🔁", "Readmissao Hospitalar 30 dias",         "SIH"),
        ("mortalidade_hospitalar","💀", "Mortalidade Hospitalar",                 "SIH + SIM"),
        ("permanencia_prolongada","🛏️", "Permanencia Prolongada",                 "SIH"),
        ("infeccao_hospitalar",   "🦠", "Infeccao Hospitalar",                    "SIH"),
        ("custo_elevado",         "💰", "Custo Hospitalar Elevado",               "SIH"),
    ],
    "Saude Materno-Infantil": [
        ("mortalidade_neonatal",  "👶", "Mortalidade Neonatal",                   "SINASC + SIM"),
        ("baixo_peso_nascer",     "⚖️", "Baixo Peso ao Nascer",                   "SINASC"),
        ("prematuridade",         "🍼", "Prematuridade",                           "SINASC"),
        ("apgar_baixo",           "❤️", "Apgar Baixo no 5 Minuto",               "SINASC"),
    ],
    "Tuberculose e Hanseniase": [
        ("abandono_tb",           "🫀", "Abandono de Tratamento TB",              "SINAN"),
        ("abandono_hanseniase",   "🩺", "Abandono de Tratamento Hanseniase",      "SINAN"),
    ],
    "Arboviroses": [
        ("dengue_grave",          "🦟", "Dengue Grave ou com Sinais de Alarme",   "SINAN"),
        ("chikungunya_hospitalizado","🦟","Hospitalizacao por Chikungunya",        "SINAN"),
    ],
    "HIV e ISTs": [
        ("obito_aids",            "🎗️", "Obito por AIDS",                         "SINAN"),
        ("sifilis_nao_cura",      "💊", "Nao-Cura de Sifilis Adquirida",          "SINAN"),
    ],
    "Violencia e Intoxicacoes": [
        ("violencia_autoprovocada","🧠", "Risco de Violencia Autoprovocada",      "SINAN"),
        ("intoxicacao_grave",     "⚠️", "Desfecho Adverso em Intoxicacao Exogena","SINAN"),
    ],
}

# ── Session state ─────────────────────────────────────────────────────────────
if "outcome_key" not in st.session_state:
    st.session_state.outcome_key = None

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Oculta elementos desnecessários */
header, footer,
[data-testid="stSidebar"], [data-testid="stSidebarNav"],
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], #MainMenu { display: none !important; }

/* Forca fundo branco em toda a app */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {
    background-color: #ffffff !important;
    color: #1e2d4a !important;
}

.block-container {
    padding: 2.5rem 3rem !important;
    max-width: 1100px !important;
}

/* Tipografia */
.ds-title {
    font-size: 2rem;
    font-weight: 700;
    color: #1e2d4a !important;
    margin-bottom: .2rem;
}
.ds-sub {
    font-size: 1rem;
    color: #6b7d9b !important;
    margin-bottom: 2rem;
}
.ds-group {
    font-size: .7rem;
    font-weight: 700;
    color: #6b7d9b !important;
    text-transform: uppercase;
    letter-spacing: .09em;
    margin: 1.5rem 0 .4rem;
}

/* Cards */
.ds-card {
    border: 1.5px solid #dce3ed;
    border-radius: 10px;
    padding: .8rem 1rem;
    margin-bottom: .5rem;
    background: #ffffff !important;
    min-height: 72px;
}
.ds-card strong {
    font-size: .85rem;
    color: #1e2d4a !important;
    display: block;
    margin-bottom: .2rem;
    line-height: 1.35;
}
.ds-card.sel {
    border-color: #1a56db;
    background: #eff6ff !important;
}
.ds-badge {
    font-size: .68rem;
    color: #6b7d9b !important;
    font-weight: 500;
}

/* Todos os botoes — base branca com borda */
div[data-testid="stButton"] > button {
    background-color: #ffffff !important;
    color: #1e2d4a !important;
    border: 1.5px solid #dce3ed !important;
    border-radius: 6px !important;
    font-size: .8rem !important;
    font-weight: 500 !important;
}
div[data-testid="stButton"] > button:hover {
    background-color: #eff6ff !important;
    border-color: #1a56db !important;
    color: #1a56db !important;
}

/* Botao primario — azul solido */
div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
    background-color: #1a56db !important;
    color: #ffffff !important;
    border-color: #1a56db !important;
}
div[data-testid="stButton"] > button[data-testid="baseButton-primary"]:hover {
    background-color: #1648c0 !important;
    border-color: #1648c0 !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="ds-title">🏥 DataSUS AI Prediction</p>', unsafe_allow_html=True)
st.markdown('<p class="ds-sub">Modelagem preditiva em saude publica — selecione o desfecho para comecar</p>', unsafe_allow_html=True)

# ── Selecao de desfecho ───────────────────────────────────────────────────────
sel = st.session_state.outcome_key

for group_name, outcomes in OUTCOME_GROUPS.items():
    st.markdown(f'<p class="ds-group">{group_name}</p>', unsafe_allow_html=True)
    cols = st.columns(len(outcomes))
    for col, (key, icon, name, source) in zip(cols, outcomes):
        with col:
            is_sel = sel == key
            cls = "ds-card sel" if is_sel else "ds-card"
            st.markdown(
                f'<div class="{cls}">'
                f'<strong>{icon} {name}</strong>'
                f'<span class="ds-badge">{source}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            label = "✓ Selecionado" if is_sel else "Selecionar"
            if st.button(label, key=f"sel_{key}",
                         type="primary" if is_sel else "secondary",
                         use_container_width=True):
                st.session_state.outcome_key = key
                st.rerun()

# ── CTA ───────────────────────────────────────────────────────────────────────
st.markdown("---")
if sel:
    st.success(f"Desfecho selecionado. Clique abaixo para iniciar a analise.")
    if st.button("Iniciar Analise →", type="primary", use_container_width=False):
        st.switch_page("pages/analise.py")
else:
    st.info("Selecione um desfecho acima para comecar a modelagem.")
