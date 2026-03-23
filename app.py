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

# ── Metadados dos desfechos ────────────────────────────────────────────────────
# status: "ok" | "dev"
# linkage: None | str  (mensagem de aviso quando requer linkage entre bases)
# est_min: tempo estimado em minutos para baixar + processar (1.000 registros)

OUTCOME_GROUPS = {
    "Internação Hospitalar": [
        {
            "key":     "readmissao_30d",
            "icon":    "sync",
            "name":    "Readmissão Hospitalar 30 dias",
            "source":  "SIH",
            "est_min": 10,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SIH. Pipeline completo disponível.",
        },
        {
            "key":     "permanencia_prolongada",
            "icon":    "bed",
            "name":    "Permanência Hospitalar Prolongada",
            "source":  "SIH",
            "est_min": 10,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SIH. Pipeline completo disponível.",
        },
        {
            "key":     "infeccao_hospitalar",
            "icon":    "coronavirus",
            "name":    "Infecção Hospitalar",
            "source":  "SIH",
            "est_min": 10,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SIH. Pipeline completo disponível.",
        },
        {
            "key":     "custo_elevado",
            "icon":    "payments",
            "name":    "Custo Hospitalar Elevado",
            "source":  "SIH",
            "est_min": 10,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SIH. Pipeline completo disponível.",
        },
        {
            "key":     "mortalidade_hospitalar",
            "icon":    "monitor_heart",
            "name":    "Mortalidade Hospitalar",
            "source":  "SIH + SIM",
            "est_min": 15,
            "status":  "dev",
            "linkage": "Requer linkage SIH ↔ SIM. Qualidade depende do pareamento por CPF/DTNASC.",
            "note":    "Linkage entre internações (SIH) e óbitos (SIM). Dados do SIM podem ter atraso de publicação.",
        },
    ],
    "Saúde Materno-Infantil": [
        {
            "key":     "baixo_peso_nascer",
            "icon":    "scale",
            "name":    "Baixo Peso ao Nascer",
            "source":  "SINASC",
            "est_min": 5,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SINASC. Pipeline completo disponível.",
        },
        {
            "key":     "prematuridade",
            "icon":    "baby_changing_station",
            "name":    "Prematuridade",
            "source":  "SINASC",
            "est_min": 5,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SINASC. Pipeline completo disponível.",
        },
        {
            "key":     "apgar_baixo",
            "icon":    "cardiology",
            "name":    "Apgar Baixo no 5º Minuto",
            "source":  "SINASC",
            "est_min": 5,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SINASC. Pipeline completo disponível.",
        },
        {
            "key":     "mortalidade_neonatal",
            "icon":    "child_care",
            "name":    "Mortalidade Neonatal",
            "source":  "SINASC + SIM",
            "est_min": 12,
            "status":  "dev",
            "linkage": "Requer linkage SINASC ↔ SIM. Pareamento por DTNASC/SEXO/PESO pode ter falhas.",
            "note":    "Linkage entre nascimentos (SINASC) e óbitos neonatais (SIM). Dados do SIM com possível atraso.",
        },
    ],
    "SINAN — Tuberculose e Hanseníase": [
        {
            "key":     "abandono_tb",
            "icon":    "pulmonology",
            "name":    "Abandono de Tratamento TB",
            "source":  "SINAN",
            "est_min": 8,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SINAN_TB. Pipeline completo disponível.",
        },
        {
            "key":     "abandono_hanseniase",
            "icon":    "stethoscope",
            "name":    "Abandono de Tratamento — Hanseníase",
            "source":  "SINAN",
            "est_min": 5,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SINAN_HANS. Pipeline completo disponível.",
        },
    ],
    "SINAN — Arboviroses": [
        {
            "key":     "dengue_grave",
            "icon":    "pest_control",
            "name":    "Dengue Grave ou com Sinais de Alarme",
            "source":  "SINAN",
            "est_min": 8,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SINAN_DENG. Pipeline completo disponível.",
        },
        {
            "key":     "chikungunya_hospitalizado",
            "icon":    "local_hospital",
            "name":    "Hospitalização por Chikungunya",
            "source":  "SINAN",
            "est_min": 6,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SINAN_CHIK. Pipeline completo disponível.",
        },
    ],
    "SINAN — HIV e ISTs": [
        {
            "key":     "obito_aids",
            "icon":    "medical_information",
            "name":    "Óbito por AIDS",
            "source":  "SINAN",
            "est_min": 5,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SINAN_AIDS. Pipeline completo disponível.",
        },
        {
            "key":     "sifilis_nao_cura",
            "icon":    "medication",
            "name":    "Não-Cura de Sífilis Adquirida",
            "source":  "SINAN",
            "est_min": 5,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SINAN_SIFA. Pipeline completo disponível.",
        },
    ],
    "SINAN — Violência e Intoxicações": [
        {
            "key":     "violencia_autoprovocada",
            "icon":    "psychology",
            "name":    "Risco de Violência Autoprovocada",
            "source":  "SINAN",
            "est_min": 10,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SINAN_VIOL. Pipeline completo disponível.",
        },
        {
            "key":     "intoxicacao_grave",
            "icon":    "warning",
            "name":    "Desfecho Adverso em Intoxicação Exógena",
            "source":  "SINAN",
            "est_min": 10,
            "status":  "ok",
            "linkage": None,
            "note":    "Base única SINAN_IEXO. Pipeline completo disponível.",
        },
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

.block-container { padding: 3rem 3rem !important; max-width: 1200px !important; }

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
.ds-sub { font-size: 0.9rem; color: #6b7280 !important; margin-bottom: .75rem; }

.ds-legend {
    display: flex; gap: 1.25rem; align-items: center;
    font-size: .75rem; color: #6b7280; margin-bottom: 2rem;
    padding: .6rem 1rem; border: 1px solid #f3f4f6;
    border-radius: 6px; background: #fafafa; width: fit-content;
}
.ds-legend-item { display: flex; align-items: center; gap: .35rem; }
.dot-ok  { width: 8px; height: 8px; border-radius: 50%; background: #22c55e; flex-shrink:0; }
.dot-dev { width: 8px; height: 8px; border-radius: 50%; background: #f97316; flex-shrink:0; }
.dot-link{ width: 8px; height: 8px; border-radius: 50%; background: #f59e0b; flex-shrink:0; }

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
    background: #ffffff !important;
    min-height: 108px;
    display: flex; flex-direction: column;
    justify-content: space-between; overflow: hidden;
    transition: border-color .12s;
}
.ds-card:hover { border-color: #9ca3af; }
.ds-card.sel { border: 1.5px solid #111827; background: #f9fafb !important; }
.ds-card.dev {
    border-color: #fed7aa; background: #fffbf5 !important;
    opacity: .9;
}
.ds-card.dev:hover { border-color: #fb923c; }
.ds-card.dev.sel { border: 1.5px solid #f97316; background: #fff7ed !important; }

.ds-card-name {
    font-size: .81rem; color: #111827 !important;
    display: flex; align-items: flex-start;
    gap: .3rem; line-height: 1.3; flex: 1; font-weight: 600;
}
.ds-card-name .ms { flex-shrink: 0; margin-top: .05rem; }

.ds-card-meta {
    display: flex; align-items: center; gap: .5rem;
    flex-wrap: wrap; margin-top: .3rem;
}
.ds-badge-src {
    font-size: .63rem; color: #9ca3af; font-weight: 500;
}
.ds-badge-time {
    font-size: .63rem; color: #6b7280; font-weight: 500;
    display: flex; align-items: center; gap: .2rem;
}
.ds-badge-dev {
    font-size: .6rem; font-weight: 700; color: #c2410c;
    background: #ffedd5; padding: 1px 6px; border-radius: 4px;
    letter-spacing: .04em;
}
.ds-badge-link {
    font-size: .6rem; font-weight: 600; color: #92400e;
    background: #fef3c7; padding: 1px 6px; border-radius: 4px;
}
.ds-card-note {
    font-size: .67rem; color: #9ca3af; margin-top: .25rem;
    line-height: 1.35; font-style: italic;
}

/* Botões */
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
    '<p class="ds-sub">Modelagem preditiva em saúde pública — selecione o desfecho para começar</p>',
    unsafe_allow_html=True,
)

# Legenda
st.markdown(
    '<div class="ds-legend">'
    '<span class="ds-legend-item"><span class="dot-ok"></span>Pipeline completo disponível</span>'
    '<span class="ds-legend-item"><span class="dot-dev"></span>Em desenvolvimento (requer linkage)</span>'
    '<span class="ds-legend-item"><span class="dot-link"></span>Linkage entre bases</span>'
    '<span style="color:#d1d5db">|</span>'
    '<span class="ds-legend-item"><span class="ms" style="font-size:.85rem;color:#6b7280">schedule</span>'
    'Tempo estimado de download + processamento (1.000 registros)</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Seleção de desfecho ───────────────────────────────────────────────────────
try:
    sel = st.session_state.outcome_key
    N_COLS = 4

    for group_name, outcomes in OUTCOME_GROUPS.items():
        # Ordena: ok primeiro, dev depois
        _sorted = sorted(outcomes, key=lambda o: (0 if o["status"] == "ok" else 1))
        st.markdown(f'<p class="ds-group">{group_name}</p>', unsafe_allow_html=True)

        for row_start in range(0, len(_sorted), N_COLS):
            row = _sorted[row_start : row_start + N_COLS]
            cols = st.columns(N_COLS)

            for col_idx, o in enumerate(row):
                key    = o["key"]
                icon   = o["icon"]
                name   = o["name"]
                source = o["source"]
                status = o["status"]
                est    = o["est_min"]
                linkage = o["linkage"]
                note   = o["note"]
                is_sel = sel == key

                # Badges extras
                dev_badge  = '<span class="ds-badge-dev">EM DESENVOLVIMENTO</span>' if status == "dev" else ""
                link_badge = '<span class="ds-badge-link">LINKAGE</span>' if linkage else ""

                # CSS da card
                card_cls = "ds-card"
                if status == "dev":
                    card_cls += " dev"
                if is_sel:
                    card_cls += " sel"

                note_html = f'<div class="ds-card-note">{note}</div>' if note else ""
                if linkage:
                    note_html += f'<div class="ds-card-note" style="color:#b45309">⚠ {linkage}</div>'

                with cols[col_idx]:
                    st.markdown(
                        f'<div class="{card_cls}">'
                        f'<div class="ds-card-name"><span class="ms">{icon}</span>{name}</div>'
                        f'<div class="ds-card-meta">'
                        f'<span class="ds-badge-src">{source}</span>'
                        f'<span class="ds-badge-time">'
                        f'<span class="ms" style="font-size:.7rem;color:#9ca3af">schedule</span>'
                        f'~{est} min</span>'
                        f'{dev_badge}{link_badge}'
                        f'</div>'
                        f'{note_html}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    btn_label = "Selecionar" if status == "ok" else "Ver (em dev.)"
                    try:
                        clicked = st.button(
                            btn_label, key=f"sel_{key}",
                            type="primary" if is_sel else "secondary",
                            use_container_width=True,
                        )
                    except TypeError:
                        clicked = st.button(
                            btn_label, key=f"sel_{key}",
                            type="primary" if is_sel else "secondary",
                        )
                    if clicked:
                        st.session_state.outcome_key = key
                        st.switch_page("pages/analise.py")

except Exception as e:
    import traceback
    st.error(f"**Erro na aplicação:** {e}")
    st.code(traceback.format_exc())
    if st.button("↺ Reiniciar sessão", type="primary"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ── Rodapé com reset de emergência ────────────────────────────────────────────
st.markdown('<hr style="border:none;border-top:1px solid #f3f4f6;margin:2.5rem 0 1rem">', unsafe_allow_html=True)
_r1, _r2 = st.columns([10, 1])
with _r2:
    if st.button("↺ Reset", help="Limpa toda a sessão e reinicia o pipeline", type="secondary"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
