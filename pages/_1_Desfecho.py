import streamlit as st
from core.outcomes import OUTCOMES, OUTCOME_GROUPS

st.set_page_config(page_title="Desfecho | DataSUS AI", page_icon="🎯", layout="wide")
st.title("🎯 Selecionar Desfecho")
st.markdown(
    "Escolha o desfecho clínico que você quer modelar. "
    "Os desfechos estão organizados por área temática."
)

current = st.session_state.get("outcome_key")

for group_name, keys in OUTCOME_GROUPS.items():
    st.subheader(group_name)
    cols = st.columns(3)
    for i, key in enumerate(keys):
        outcome = OUTCOMES.get(key)
        if outcome is None:
            continue
        with cols[i % 3]:
            selected = current == key
            border = "2px solid #1f77b4" if selected else "1px solid #ddd"
            bg = "#f0f7ff" if selected else "#fafafa"
            st.markdown(
                f"""
                <div style="border:{border};border-radius:10px;padding:16px;margin-bottom:12px;background:{bg}">
                    <h4 style="margin:0">{outcome.icon} {outcome.name}</h4>
                    <p style="color:#555;font-size:0.85em;margin:6px 0">{outcome.description[:140]}…</p>
                    <p style="margin:3px 0;font-size:0.85em"><b>Dados:</b> {', '.join(outcome.data_sources)}</p>
                    <p style="margin:3px 0;font-size:0.85em"><b>Janela:</b> {outcome.prediction_window_days} dias &nbsp;|&nbsp; <b>Download:</b> ~{outcome.estimated_download_min} min</p>
                    {'<span style="color:#1f77b4;font-weight:bold">✓ Selecionado</span>' if selected else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Selecionar", key=f"btn_{key}", use_container_width=True):
                st.session_state["outcome_key"] = key
                st.session_state["raw_data"] = {}
                st.session_state["cohort"] = None
                st.session_state["model_results"] = None
                st.rerun()
    st.divider()

if current:
    st.success(f"Desfecho selecionado: **{OUTCOMES[current].name}** — vá para a página 📥 Dados.")
else:
    st.info("Selecione um desfecho acima para continuar.")
