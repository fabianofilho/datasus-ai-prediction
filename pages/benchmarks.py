"""DataSUS AI Prediction — Catálogo de benchmarks (datasets externos)."""
from pathlib import Path
from PIL import Image as _PILImage
import streamlit as st

from core.data.benchmarks import BENCHMARK_GROUPS, BENCHMARKS

_favicon = _PILImage.open(Path(__file__).parent.parent / "favicon.png")
st.set_page_config(
    page_title="Benchmarks — DataSUS AI Prediction",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

_PIPELINE_KEYS = [
    "raw_data", "cohort", "feature_config", "treatment_config",
    "model_config", "model_results", "calib_results", "upload_df",
    "upload_target", "upload_features", "upload_dict", "X_res",
]


def _reset_pipeline():
    for _rk in _PIPELINE_KEYS:
        if _rk in st.session_state:
            st.session_state[_rk] = {} if _rk == "raw_data" else None


def _go_benchmark(bench_key: str):
    bench = BENCHMARKS[bench_key]
    df = bench.loader()
    _reset_pipeline()
    ss = st.session_state
    ss.outcome_key = "__diy__"
    ss.upload_df = df
    ss.upload_target = bench.target_col
    ss.upload_features = [c for c in df.columns if c != bench.target_col]
    ss.upload_dict = bench.dict_meta or {}
    ss.raw_data = {}
    st.switch_page("pages/analise.py")


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

.block-container { padding: 3rem 3rem !important; max-width: 1200px !important; }

.ms { font-family: 'Material Symbols Outlined'; font-style: normal; font-weight: normal;
    font-size: 1rem; line-height: 1; vertical-align: middle; display: inline-block; color: #111827; }
.ms-lg { font-size: 1.4rem; margin-right: .25rem; }

h1,h2,h3,h4,h5,h6 { font-family:"Space Grotesk","Inter",sans-serif !important; letter-spacing:-.01em; }
.ds-title {
    font-family: "Space Grotesk", "Inter", sans-serif;
    font-size: 1.6rem; font-weight: 700;
    color: #223886 !important; margin-bottom: .15rem;
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
.dot-ok       { width: 8px; height: 8px; border-radius: 50%; background: #22c55e; flex-shrink:0; }
.dot-external { width: 8px; height: 8px; border-radius: 50%; background: #6b7280; flex-shrink:0; }

.ds-group {
    font-size: .68rem; font-weight: 700;
    color: #9ca3af !important; text-transform: uppercase;
    letter-spacing: .1em; margin: 1.75rem 0 .5rem;
    padding-bottom: .35rem; border-bottom: 1px solid #f3f4f6;
}

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
.ds-card.external { border-color: #e5e7eb; background: #f9fafb !important; opacity: .9; }
.ds-card.external:hover { border-color: #6b7280; }

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
.ds-badge-src { font-size: .63rem; color: #9ca3af; font-weight: 500; }
.ds-badge-time { font-size: .63rem; color: #6b7280; font-weight: 500;
    display: flex; align-items: center; gap: .2rem; }
.ds-badge-external { font-size: .6rem; font-weight: 700; color: #374151;
    background: #e5e7eb; padding: 1px 6px; border-radius: 4px; letter-spacing: .04em; }
.ds-card-note { font-size: .67rem; color: #9ca3af; margin-top: .25rem;
    line-height: 1.35; font-style: italic; }

div[data-testid="stButton"] { display: flex !important; justify-content: flex-start !important; }
div[data-testid="stButton"] > button {
    background-color: #ffffff !important; color: #111827 !important;
    border: 1px solid #e5e7eb !important; border-radius: 6px !important;
    font-size: .8rem !important; font-weight: 500 !important;
    padding: 5px 16px !important; width: auto !important;
    transition: all .12s !important;
}
div[data-testid="stButton"] > button:hover {
    background-color: #eef1fb !important; border-color: #223886 !important;
}
div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
    background-color: #223886 !important; color: #ffffff !important;
    border-color: #223886 !important; font-weight: 600 !important;
    border-bottom: 3px solid #9ec83b !important;
}
div[data-testid="stButton"] > button[data-testid="baseButton-primary"]:hover {
    background-color: #1a2b66 !important; border-color: #1a2b66 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Voltar ────────────────────────────────────────────────────────────────────
_back_col, _ = st.columns([1, 9])
with _back_col:
    if st.button("← Voltar", key="bench_back"):
        st.switch_page("app.py")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<p class="ds-title">'
    '<span class="ms ms-lg">analytics</span>'
    'BENCHMARKS'
    '</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="ds-sub">Datasets de saúde abertos para rodar o mesmo pipeline em referências internacionais.</p>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="ds-legend">'
    '<span class="ds-legend-item"><span class="dot-ok"></span>Loader pronto, entra direto no pipeline</span>'
    '<span class="ds-legend-item"><span class="dot-external"></span>Catálogo externo, requer ETL ou credencial</span>'
    '<span style="color:#d1d5db">|</span>'
    '<span class="ds-legend-item"><span class="ms" style="font-size:.85rem;color:#6b7280">schedule</span>'
    'Tempo estimado de download + parse</span>'
    '</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-size:.8rem;color:#6b7280;margin:-1rem 0 1.5rem">'
    'Catálogo curado a partir do '
    '<a href="https://github.com/fabianofilho/awesome-health-datasets" target="_blank" '
    'style="color:#223886;text-decoration:none;border-bottom:1px dotted #223886">awesome-health-datasets</a>. '
    'Benchmarks tabulares clássicos rodam no mesmo pipeline DIY; demais ficam como referência.'
    '</p>',
    unsafe_allow_html=True,
)

N_COLS = 3
for group_name, benches in BENCHMARK_GROUPS.items():
    st.markdown(f'<p class="ds-group">{group_name}</p>', unsafe_allow_html=True)

    for row_start in range(0, len(benches), N_COLS):
        row = benches[row_start : row_start + N_COLS]
        cols = st.columns(N_COLS)

        for col_idx, b in enumerate(row):
            card_cls = "ds-card"
            if b.status == "external":
                card_cls += " external"

            ext_badge = '<span class="ds-badge-external">EXTERNO</span>' if b.status == "external" else ""

            with cols[col_idx]:
                st.markdown(
                    f'<div class="{card_cls}">'
                    f'<div class="ds-card-name"><span class="ms">{b.icon}</span>{b.name}</div>'
                    f'<div class="ds-card-meta">'
                    f'<span class="ds-badge-src">{b.source}</span>'
                    f'<span class="ds-badge-time">'
                    f'<span class="ms" style="font-size:.7rem;color:#9ca3af">schedule</span>'
                    f'~{b.est_min} min</span>'
                    f'{ext_badge}'
                    f'</div>'
                    f'<div class="ds-card-note">{b.note}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                if b.status == "ok":
                    if st.button("Carregar e rodar", key=f"bench_{b.key}", type="primary", use_container_width=True):
                        with st.spinner(f"Baixando {b.name}..."):
                            _go_benchmark(b.key)
                else:
                    st.link_button("Abrir fonte", b.url, use_container_width=True)
