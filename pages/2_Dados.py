import pandas as pd
import streamlit as st

from core.data.downloader import (
    STATES, cached_files,
    ManualUploadRequired, load_from_csv,
)
from core.outcomes import OUTCOMES

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
    selected_states = st.multiselect("Estados (UF)", options=STATES, default=["SP"])
with col2:
    years = list(range(2018, 2024))
    selected_years = st.multiselect("Anos", options=years, default=[2023])

st.divider()

cached = cached_files()
if cached:
    with st.expander(f"📂 Arquivos em cache local ({len(cached)} arquivos)"):
        st.write(sorted(cached))

if not selected_states or not selected_years:
    st.info("Selecione pelo menos um estado e um ano.")
    st.stop()

# ── Download automático ────────────────────────────────────────────────────────
if st.button("⬇️ Baixar / Carregar Dados", type="primary", use_container_width=True):
    raw_data = {}
    manual_needed = []

    for source in outcome.data_sources:
        progress = st.progress(0.0, text=f"Iniciando {source}...")
        try:
            def cb(pct, msg, _p=progress):
                _p.progress(min(pct, 1.0), text=msg)

            dfs = []
            for state in selected_states:
                for year in selected_years:
                    from core.data.downloader import fetch
                    dfs.append(fetch(source, state, year, cb))

            df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
            raw_data[source] = df
            progress.progress(1.0, text=f"✅ {source}: {len(df):,} registros")

        except ManualUploadRequired as e:
            progress.empty()
            manual_needed.append((source, selected_states, selected_years, e.reasons))

    if raw_data:
        st.session_state["raw_data"] = raw_data
        st.session_state["cohort"] = None
        st.session_state["model_results"] = None

    if manual_needed:
        st.session_state["manual_needed"] = manual_needed
    elif "manual_needed" in st.session_state:
        del st.session_state["manual_needed"]

    if raw_data and not manual_needed:
        st.success("✅ Todos os dados carregados! Vá para 🔬 Cohort.")

# ── Upload manual (fallback) ───────────────────────────────────────────────────
manual_needed = st.session_state.get("manual_needed", [])
if manual_needed:
    st.divider()
    st.warning("⚠️ Download automático falhou. Verifique os erros abaixo ou faça upload manual dos CSVs.")

    with st.expander("📖 Como baixar do TABNET", expanded=True):
        st.markdown("""
**Para cada fonte de dados:**

1. Acesse **TABNET DataSUS**: http://tabnet.datasus.gov.br
2. Selecione o sistema correto:
   - **SIH** → Epidemiológicas e Morbidade → SIH-SUS → Produção Hospitalar
   - **SIM** → Estatísticas Vitais → Mortalidade
   - **SINASC** → Estatísticas Vitais → Nascidos Vivos
   - **SINAN-TB** → Epidemiológicas e Morbidade → SINAN → Tuberculose
3. Filtre por estado e ano → **Mostra**
4. Clique em **Copia como .CSV** ou baixe o arquivo
5. Faça upload abaixo

> **Alternativa:** Baixe os arquivos .dbc do FTP do DataSUS e converta
> com o utilitário **TabWin** (Windows) ou **dbc2dbf** (Linux/Mac).
        """)

    raw_data = st.session_state.get("raw_data", {})

    for (source, states, years_list, reasons) in manual_needed:
        st.subheader(f"Upload: {source}")
        if reasons:
            with st.expander("🔍 Detalhes do erro"):
                for r in reasons:
                    st.code(r)

        uploaded = st.file_uploader(
            f"Faça upload do CSV do {source} ({', '.join(states)}, {years_list})",
            type=["csv", "txt"],
            key=f"upload_{source}",
        )
        if uploaded:
            try:
                df = load_from_csv(
                    uploaded.read(),
                    source,
                    states[0] if len(states) == 1 else "BR",
                    years_list[0] if len(years_list) == 1 else 0,
                )
                raw_data[source] = df
                st.success(f"✅ {source}: {len(df):,} registros carregados do CSV.")
                st.session_state["raw_data"] = raw_data
                st.session_state["cohort"] = None
            except Exception as e:
                st.error(f"Erro ao processar CSV: {e}")

    if set(outcome.data_sources) <= set(raw_data.keys()):
        st.success("✅ Todos os dados carregados! Vá para 🔬 Cohort.")

# ── Preview dos dados carregados ──────────────────────────────────────────────
if st.session_state.get("raw_data"):
    st.divider()
    st.subheader("Preview dos dados")
    for src, df in st.session_state["raw_data"].items():
        with st.expander(f"{src} — {len(df):,} registros, {df.shape[1]} colunas"):
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"Colunas: {', '.join(df.columns.tolist()[:30])}{'...' if len(df.columns) > 30 else ''}")
