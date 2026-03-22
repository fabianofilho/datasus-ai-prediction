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
        ("abandono_tb",           "🫁", "Abandono de Tratamento TB",              "SINAN"),
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

# ── CSS minimo ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
header, footer, [data-testid="stSidebar"],
[data-testid="stSidebarNav"], [data-testid="stHeader"],
[data-testid="stToolbar"], [data-testid="stDecoration"],
#MainMenu { display: none !important; }

.block-container { padding: 2rem 3rem !important; max-width: 1100px !important; }

.ds-title { font-size: 2rem; font-weight: 700; color: #1e2d4a; margin-bottom: .25rem; }
.ds-sub   { color: #6b7d9b; margin-bottom: 2rem; }
.ds-group { font-size: .75rem; font-weight: 700; color: #6b7d9b;
            text-transform: uppercase; letter-spacing: .08em;
            margin: 1.5rem 0 .5rem; }
.ds-card  { border: 1px solid #dce3ed; border-radius: 8px; padding: .75rem 1rem;
            cursor: pointer; margin-bottom: .5rem; background: #fff; }
.ds-card:hover { border-color: #1a56db; background: #eff6ff; }
.ds-card.sel   { border-color: #1a56db; background: #eff6ff; }
.ds-badge { font-size: .7rem; color: #6b7d9b; }
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
                f'<strong>{icon} {name}</strong><br>'
                f'<span class="ds-badge">{source}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            label = "Selecionado" if is_sel else "Selecionar"
            if st.button(label, key=f"sel_{key}",
                         type="primary" if is_sel else "secondary",
                         use_container_width=True):
                st.session_state.outcome_key = key
                st.rerun()

# ── CTA ───────────────────────────────────────────────────────────────────────
st.markdown("---")
if sel:
    st.success(f"Desfecho selecionado. Abra **Analise** no menu para continuar.")
    if st.button("Iniciar Analise →", type="primary", use_container_width=False):
        st.switch_page("pages/analise.py")
else:
    st.info("Selecione um desfecho acima para comecar a modelagem.")
