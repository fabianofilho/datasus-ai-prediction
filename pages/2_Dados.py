import streamlit as st
import pandas as pd
from core.outcomes import OUTCOMES
from core.data.downloader import STATES, fetch_multi, cached_files

st.set_page_config(page_title="Dados | DataSUS AI", page_icon="📥", layout="wide")
st.title("📥 Baixar Dados")

outcome_key = st.session_state.get("outcome_key")
if not outcome_key:
    st.warning("Selecione um desfecho primeiro na página 🎯 Desfecho.")
    st.stop()

outcome = OUTCOMES[outcome_key]
st.markdown(f"**Desfecho:** {outcome.icon} {outcome.name}")
st.markdown(f"**Dados necessários:** {', '.join(outcome.data_sources)}")

st.divider()

col1, col2 = st.columns(2)
with col1:
    selected_states = st.multiselect(
        "Estados (UF)",
        options=STATES,
        default=["SP"],
        help="Selecione um ou mais estados. Mais estados = download mais lento.",
    )
with col2:
    current_year = 2023
    years = list(range(2018, current_year + 1))
    selected_years = st.multiselect(
        "Anos",
        options=years,
        default=[current_year],
        help="Selecione um ou mais anos.",
    )

st.divider()

# Show already cached files
cached = cached_files()
if cached:
    with st.expander(f"📂 Arquivos em cache local ({len(cached)} arquivos)"):
        st.write(sorted(cached))

if not selected_states or not selected_years:
    st.info("Selecione pelo menos um estado e um ano.")
    st.stop()

total = len(selected_states) * len(selected_years) * len(outcome.data_sources)
st.info(f"Serão baixados até **{total}** arquivos (alguns podem já estar em cache).")

if st.button("⬇️ Baixar / Carregar Dados", type="primary", use_container_width=True):
    raw_data = {}
    progress = st.progress(0)
    status = st.empty()

    n_sources = len(outcome.data_sources)
    for si, source in enumerate(outcome.data_sources):
        status.text(f"Baixando {source}...")
        try:
            def cb(pct, msg, _s=source, _si=si, _n=n_sources):
                overall = (_si + pct) / _n
                progress.progress(overall)
                status.text(f"{_s}: {msg}")

            df = fetch_multi(source, selected_states, selected_years, progress_callback=cb)
            raw_data[source] = df
            progress.progress((_si + 1) / n_sources)
            status.text(f"✅ {source}: {len(df):,} registros carregados.")
        except Exception as e:
            st.error(f"Erro ao baixar {source}: {e}")

    if raw_data:
        st.session_state["raw_data"] = raw_data
        st.session_state["cohort"] = None
        st.session_state["model_results"] = None
        progress.progress(1.0)
        status.text("✅ Download concluído!")
        st.success("Dados carregados. Vá para 🔬 Cohort para construir a coorte.")

# Preview loaded data
if st.session_state.get("raw_data"):
    st.divider()
    st.subheader("Preview dos dados")
    for src, df in st.session_state["raw_data"].items():
        with st.expander(f"{src} — {len(df):,} registros, {df.shape[1]} colunas"):
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"Colunas: {', '.join(df.columns.tolist())}")
