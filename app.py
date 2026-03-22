"""DataSUS AI Prediction — home page minima, zero imports pesados."""
import streamlit as st

st.set_page_config(
    page_title="DataSUS AI Prediction",
    page_icon="🏥",
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
    "Tuberculose e Hanseniase": [
        ("abandono_tb",              "pulmonology",         "Abandono de Tratamento TB",               "SINAN"),
        ("abandono_hanseniase",      "stethoscope",         "Abandono de Tratamento Hanseniase",       "SINAN"),
    ],
    "Arboviroses": [
        ("dengue_grave",             "pest_control",        "Dengue Grave ou com Sinais de Alarme",    "SINAN"),
        ("chikungunya_hospitalizado","local_hospital",      "Hospitalizacao por Chikungunya",          "SINAN"),
    ],
    "HIV e ISTs": [
        ("obito_aids",               "medical_information", "Obito por AIDS",                          "SINAN"),
        ("sifilis_nao_cura",         "medication",          "Nao-Cura de Sifilis Adquirida",           "SINAN"),
    ],
    "Violencia e Intoxicacoes": [
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
/* Oculta elementos desnecessários */
header, footer,
[data-testid="stSidebar"], [data-testid="stSidebarNav"],
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], #MainMenu { display: none !important; }

/* Fundo branco em toda a app */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {
    background-color: #ffffff !important;
    color: #1e2d4a !important;
}

.block-container {
    padding: 2.5rem 3rem !important;
    max-width: 1100px !important;
}

/* Material Symbols */
.ms {
    font-family: 'Material Symbols Outlined';
    font-style: normal;
    font-weight: normal;
    font-size: 1.1rem;
    line-height: 1;
    vertical-align: middle;
    display: inline-block;
    color: #1a56db;
}
.ms-lg {
    font-size: 1.6rem;
    margin-right: .3rem;
}

/* Tipografia */
.ds-title {
    font-size: 1.9rem;
    font-weight: 700;
    color: #1e2d4a !important;
    margin-bottom: .2rem;
    display: flex;
    align-items: center;
    gap: .4rem;
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

/* Cards — altura fixa + flex para badge sempre na base */
.ds-card {
    border: 1.5px solid #dce3ed;
    border-radius: 10px;
    padding: .75rem 1rem;
    margin-bottom: .5rem;
    background: #ffffff !important;
    height: 88px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
}
.ds-card strong {
    font-size: .82rem;
    color: #1e2d4a !important;
    display: flex;
    align-items: flex-start;
    gap: .3rem;
    line-height: 1.3;
    flex: 1;
}
.ds-card strong .ms {
    flex-shrink: 0;
    margin-top: .05rem;
}
.ds-card.sel {
    border-color: #1a56db;
    background: #eff6ff !important;
}
.ds-card.sel .ms { color: #1a56db; }
.ds-badge {
    font-size: .68rem;
    color: #6b7d9b !important;
    font-weight: 500;
    margin-top: .2rem;
}

/* Botoes — base branca */
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

    for group_name, outcomes in OUTCOME_GROUPS.items():
        st.markdown(f'<p class="ds-group">{group_name}</p>', unsafe_allow_html=True)
        cols = st.columns(len(outcomes))
        for col, (key, icon, name, source) in zip(cols, outcomes):
            with col:
                is_sel = sel == key
                cls = "ds-card sel" if is_sel else "ds-card"
                st.markdown(
                    f'<div class="{cls}">'
                    f'<strong><span class="ms">{icon}</span>{name}</strong>'
                    f'<span class="ds-badge">{source}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                label = "Selecionado" if is_sel else "Selecionar"
                try:
                    clicked = st.button(label, key=f"sel_{key}",
                                        type="primary" if is_sel else "secondary",
                                        use_container_width=True)
                except TypeError:
                    clicked = st.button(label, key=f"sel_{key}",
                                        type="primary" if is_sel else "secondary")
                if clicked:
                    st.session_state.outcome_key = key
                    st.rerun()

    # ── CTA ───────────────────────────────────────────────────────────────────
    st.markdown("---")
    if sel:
        st.success("Desfecho selecionado. Clique abaixo para iniciar a analise.")
        try:
            cta = st.button("Iniciar Analise", type="primary", use_container_width=False)
        except TypeError:
            cta = st.button("Iniciar Analise", type="primary")
        if cta:
            st.switch_page("pages/analise.py")
    else:
        st.info("Selecione um desfecho acima para comecar a modelagem.")

except Exception as e:
    import traceback
    st.error(f"**Erro na aplicacao:** {e}")
    st.code(traceback.format_exc())
