"""DataSUS AI Prediction — home minimal: 3 cards para escolher a fonte de dados."""
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


if "outcome_key" not in st.session_state:
    st.session_state.outcome_key = None


_PIPELINE_KEYS = [
    "raw_data", "cohort", "feature_config", "treatment_config",
    "model_config", "model_results", "calib_results", "upload_df",
    "upload_target", "upload_features", "upload_dict", "X_res",
]


def _reset_pipeline():
    for _rk in _PIPELINE_KEYS:
        if _rk in st.session_state:
            st.session_state[_rk] = {} if _rk == "raw_data" else None


# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,300,0,0" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" />

<style>
header, footer,
[data-testid="stSidebar"], [data-testid="stSidebarNav"],
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], #MainMenu { display: none !important; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {
    background-color: #ffffff !important;
    color: #111827 !important;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

.block-container { padding: 4.5rem 3rem 3rem !important; max-width: 1160px !important; }

.ms {
    font-family: 'Material Symbols Outlined';
    font-style: normal; font-weight: normal;
    line-height: 1; display: inline-block; color: #111827;
}
h1,h2,h3,h4,h5,h6 { font-family:"Space Grotesk","Inter",sans-serif !important; letter-spacing:-.01em; }

.home-title {
    font-family: "Space Grotesk", "Inter", sans-serif;
    font-size: 2rem; font-weight: 700;
    color: #223886 !important;
    margin: 0 0 .5rem;
    display: flex; align-items: center; gap: .5rem;
}
.home-title .ms { font-size: 2rem; color: #223886; }
.home-sub {
    font-size: 1rem; color: #6b7280 !important;
    margin: 0 0 3rem;
    max-width: 640px; line-height: 1.55;
}

/* ── Cards grandes ─────────────────────────────────────────────── */
.home-card {
    border: 1px solid #e5e7eb; border-radius: 10px;
    padding: 1.75rem 1.5rem 1.25rem; background: #ffffff !important;
    min-height: 270px;
    display: flex; flex-direction: column;
    transition: border-color .15s, transform .15s, box-shadow .15s;
    margin-bottom: .75rem;
}
.home-card:hover {
    border-color: #223886;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px -10px rgba(34, 56, 134, 0.15);
}

.home-card-icon {
    width: 48px; height: 48px;
    border-radius: 10px;
    background: #eef1fb;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 1rem;
}
.home-card-icon .ms { font-size: 1.75rem; color: #223886; }

.home-card-title {
    font-family: "Space Grotesk", "Inter", sans-serif;
    font-size: 1.05rem; font-weight: 700;
    color: #111827 !important;
    margin: 0 0 .35rem;
    letter-spacing: .02em;
}
.home-card-tag {
    font-size: .65rem; font-weight: 700;
    color: #223886 !important;
    letter-spacing: .12em; text-transform: uppercase;
    margin-bottom: .75rem;
}
.home-card-desc {
    font-size: .85rem; color: #4b5563 !important;
    line-height: 1.55;
    flex: 1; margin: 0 0 1rem;
}
.home-card-meta {
    font-size: .72rem; color: #9ca3af;
    border-top: 1px solid #f3f4f6;
    padding-top: .65rem; margin-top: auto;
    display: flex; align-items: center; gap: .35rem;
}
.home-card-meta .ms { font-size: .9rem; color: #9ca3af; }

/* ── Botão dentro do card ──────────────────────────────────── */
div[data-testid="stButton"] { display: flex !important; justify-content: flex-start !important; }
div[data-testid="stButton"] > button {
    background-color: #223886 !important; color: #ffffff !important;
    border: 1px solid #223886 !important;
    border-bottom: 3px solid #9ec83b !important;
    border-radius: 6px !important;
    font-size: .85rem !important; font-weight: 600 !important;
    padding: .5rem 1.2rem !important; width: auto !important;
    transition: all .12s !important;
    font-family: "Inter", sans-serif !important;
}
div[data-testid="stButton"] > button:hover {
    background-color: #1a2b66 !important; border-color: #1a2b66 !important;
}
div[data-testid="stButton"] > button[kind="secondary"],
div[data-testid="stButton"] > button[data-testid="baseButton-secondary"] {
    background-color: #ffffff !important; color: #6b7280 !important;
    border: 1px solid #e5e7eb !important; border-bottom: 1px solid #e5e7eb !important;
    font-weight: 500 !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover,
div[data-testid="stButton"] > button[data-testid="baseButton-secondary"]:hover {
    background-color: #f9fafb !important; border-color: #9ca3af !important; color: #111827 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<p class="home-title">'
    '<span class="ms">local_hospital</span>'
    'DataSUS AI Prediction'
    '</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="home-sub">'
    'Plataforma de modelagem preditiva em saúde pública. '
    'Escolha uma fonte de dados e rode o pipeline completo: coorte, '
    'features, treino, calibração e relatório.'
    '</p>',
    unsafe_allow_html=True,
)


# ── 3 Cards ───────────────────────────────────────────────────────────────────
def _go_datasus():
    st.switch_page("pages/datasus.py")


def _go_diy():
    st.session_state.outcome_key = "__diy__"
    _reset_pipeline()
    st.switch_page("pages/upload.py")


def _go_benchmarks():
    st.switch_page("pages/benchmarks.py")


CARDS = [
    {
        "tag":   "Bases brasileiras",
        "icon":  "local_hospital",
        "title": "DATASUS",
        "desc":  "16 desfechos prontos sobre SINASC, SIH, SIM e SINAN. "
                 "Coorte, linkage e dicionário de variáveis automáticos.",
        "meta":  "Pipeline completo • 1 a 15 min",
        "btn":   "Explorar desfechos",
        "go":    _go_datasus,
    },
    {
        "tag":   "Sua base",
        "icon":  "construction",
        "title": "DIY",
        "desc":  "Carregue qualquer dataset tabular em CSV ou Parquet, "
                 "defina o desfecho binário e rode o pipeline completo.",
        "meta":  "Upload • CSV ou Parquet",
        "btn":   "Carregar minha base",
        "go":    _go_diy,
    },
    {
        "tag":   "Datasets abertos",
        "icon":  "analytics",
        "title": "BENCHMARKS",
        "desc":  "Datasets clássicos de saúde (UCI, PhysioNet) prontos para "
                 "comparar performance internacionalmente.",
        "meta":  "Pima, Heart UCI e mais • ~1 min",
        "btn":   "Ver benchmarks",
        "go":    _go_benchmarks,
    },
]

cols = st.columns(3, gap="medium")
for col, card in zip(cols, CARDS):
    with col:
        st.markdown(
            f'<div class="home-card">'
            f'<div class="home-card-icon"><span class="ms">{card["icon"]}</span></div>'
            f'<p class="home-card-tag">{card["tag"]}</p>'
            f'<p class="home-card-title">{card["title"]}</p>'
            f'<p class="home-card-desc">{card["desc"]}</p>'
            f'<div class="home-card-meta">'
            f'<span class="ms">schedule</span>{card["meta"]}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button(card["btn"], key=f"home_{card['title'].lower()}", type="primary", use_container_width=True):
            card["go"]()


# ── Rodapé ────────────────────────────────────────────────────────────────────
st.markdown('<hr style="border:none;border-top:1px solid #f3f4f6;margin:3rem 0 1rem">', unsafe_allow_html=True)
_, _r = st.columns([9, 1])
with _r:
    if st.button("↺ Reset", key="home_reset", help="Limpa toda a sessão e reinicia o pipeline"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
