import streamlit as st
from core.outcomes import OUTCOMES

st.set_page_config(page_title="Desfecho | DataSUS AI", page_icon="🎯", layout="wide")
st.title("🎯 Selecionar Desfecho")
st.markdown("Escolha o desfecho clínico que você quer modelar. Cada card mostra os dados necessários e a complexidade da tarefa.")

current = st.session_state.get("outcome_key")

cols = st.columns(2)
for i, (key, outcome) in enumerate(OUTCOMES.items()):
    with cols[i % 2]:
        selected = current == key
        border = "2px solid #1f77b4" if selected else "1px solid #ddd"
        st.markdown(
            f"""
            <div style="border:{border};border-radius:10px;padding:18px;margin-bottom:14px;background:{'#f0f7ff' if selected else '#fafafa'}">
                <h3 style="margin:0">{outcome.icon} {outcome.name}</h3>
                <p style="color:#555;font-size:0.9em;margin:8px 0">{outcome.description}</p>
                <p style="margin:4px 0"><b>Dados:</b> {', '.join(outcome.data_sources)}</p>
                <p style="margin:4px 0"><b>Janela predição:</b> {outcome.prediction_window_days} dias</p>
                <p style="margin:4px 0"><b>Download estimado:</b> ~{outcome.estimated_download_min} min</p>
                {'<span style="color:#1f77b4;font-weight:bold">✓ Selecionado</span>' if selected else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(f"Selecionar: {outcome.name}", key=f"btn_{key}", use_container_width=True):
            st.session_state["outcome_key"] = key
            st.session_state["raw_data"] = {}
            st.session_state["cohort"] = None
            st.session_state["model_results"] = None
            st.rerun()

if current:
    st.success(f"Desfecho selecionado: **{OUTCOMES[current].name}** — vá para a página 📥 Dados.")
else:
    st.info("Selecione um desfecho acima para continuar.")
