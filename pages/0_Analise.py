"""Página única de análise — fluxo sequencial em 5 etapas."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from core.data.downloader import (
    STATES,
    ManualUploadRequired,
    fetch,
    load_from_csv,
)
from core.features.cohort import CohortBuilder
from core.models import evaluation as ev
from core.models.pipeline import ALGORITHMS, train_cv
from core.outcomes import OUTCOME_GROUPS, OUTCOMES

st.set_page_config(
    page_title="DataSUS AI — Análise",
    page_icon="🏥",
    layout="wide",
)

# ── Session state ─────────────────────────────────────────────────────────────
ss = st.session_state
_defaults = {
    "outcome_key": None,
    "raw_data": {},
    "cohort": None,
    "model_results": None,
    "sel_states": ["SP"],
    "sel_years": [2023],
    "manual_needed": [],
}
for k, v in _defaults.items():
    if k not in ss:
        ss[k] = v

# ── Step tracker ──────────────────────────────────────────────────────────────
def current_step() -> int:
    if ss["model_results"]:
        return 5
    if ss["cohort"] is not None:
        return 4
    if ss["raw_data"]:
        return 3
    if ss["outcome_key"]:
        return 2
    return 1


def _step_html(n: int, label: str, step: int) -> str:
    if n < step:
        color, dot = "#22c55e", "✓"
    elif n == step:
        color, dot = "#3b82f6", "●"
    else:
        color, dot = "#d1d5db", "○"
    weight = "bold" if n <= step else "normal"
    return (
        f'<span style="color:{color};font-weight:{weight};white-space:nowrap">'
        f"{dot} {n}. {label}</span>"
    )


def render_step_bar(step: int) -> None:
    arrow = '<span style="color:#9ca3af;margin:0 6px">›</span>'
    labels = ["Desfecho", "Dados", "Coorte", "Modelo", "Resultados"]
    parts = arrow.join(_step_html(i + 1, lbl, step) for i, lbl in enumerate(labels))
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:0;'
        f'padding:12px 0 16px;font-size:0.95em">{parts}</div>',
        unsafe_allow_html=True,
    )


def section_header(icon: str, title: str, done: bool = False) -> None:
    color = "#22c55e" if done else "#3b82f6"
    check = "✅" if done else icon
    st.markdown(
        f'<h3 style="margin:0 0 12px;color:{color}">{check} {title}</h3>',
        unsafe_allow_html=True,
    )


def compact_row(label: str, value: str, change_key: str, reset_keys: list[str]) -> bool:
    col1, col2 = st.columns([10, 1])
    with col1:
        st.markdown(
            f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;'
            f'padding:10px 16px;margin-bottom:4px">'
            f'<span style="color:#166534;font-weight:600">{label}</span> '
            f'<span style="color:#374151">{value}</span></div>',
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("✏️", key=change_key, help="Alterar"):
            for k in reset_keys:
                ss[k] = _defaults[k]
            st.rerun()
    return False


# ═════════════════════════════════════════════════════════════════════════════
step = current_step()
st.markdown("## 🔬 DataSUS AI — Pipeline de Análise")
render_step_bar(step)
st.markdown('<hr style="margin:0 0 24px">', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 1 — DESFECHO
# ═════════════════════════════════════════════════════════════════════════════
with st.container():
    if ss["outcome_key"]:
        o = OUTCOMES[ss["outcome_key"]]
        compact_row(
            "🎯 Desfecho:",
            f"{o.icon} **{o.name}** — {', '.join(o.data_sources)}",
            "chg_outcome",
            ["outcome_key", "raw_data", "cohort", "model_results", "manual_needed"],
        )
    else:
        section_header("🎯", "Passo 1 — Selecionar Desfecho")
        for group_name, keys in OUTCOME_GROUPS.items():
            st.markdown(
                f'<p style="font-size:0.9em;font-weight:600;color:#6b7280;'
                f'margin:16px 0 8px;text-transform:uppercase;letter-spacing:.05em">'
                f"{group_name}</p>",
                unsafe_allow_html=True,
            )
            cols = st.columns(min(len(keys), 3))
            for i, key in enumerate(keys):
                outcome = OUTCOMES.get(key)
                if not outcome:
                    continue
                with cols[i % 3]:
                    is_sel = ss["outcome_key"] == key
                    border = "2px solid #3b82f6" if is_sel else "1px solid #e5e7eb"
                    bg = "#eff6ff" if is_sel else "#fafafa"
                    st.markdown(
                        f'<div style="border:{border};border-radius:10px;padding:14px 16px;'
                        f'margin-bottom:8px;background:{bg};min-height:110px">'
                        f'<b style="font-size:0.95em">{outcome.icon} {outcome.name}</b><br>'
                        f'<span style="color:#6b7280;font-size:0.78em;line-height:1.4">'
                        f'{outcome.description[:110]}…</span><br>'
                        f'<span style="color:#9ca3af;font-size:0.76em">'
                        f'📦 {", ".join(outcome.data_sources)} &nbsp;|&nbsp; '
                        f'⏱ ~{outcome.estimated_download_min} min</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        "✓ Selecionado" if is_sel else "Selecionar",
                        key=f"sel_{key}",
                        use_container_width=True,
                        type="primary" if is_sel else "secondary",
                    ):
                        for k in ["raw_data", "cohort", "model_results", "manual_needed"]:
                            ss[k] = _defaults[k]
                        ss["outcome_key"] = key
                        st.rerun()
        st.stop()

st.markdown('<hr style="margin:16px 0">', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 2 — DADOS
# ═════════════════════════════════════════════════════════════════════════════
outcome = OUTCOMES[ss["outcome_key"]]

with st.container():
    if ss["raw_data"]:
        summary = " | ".join(
            f"{src}: {len(df):,} registros" for src, df in ss["raw_data"].items()
        )
        compact_row(
            "📥 Dados:",
            summary,
            "chg_data",
            ["raw_data", "cohort", "model_results", "manual_needed"],
        )
        with st.expander("Ver preview dos dados"):
            for src, df in ss["raw_data"].items():
                st.caption(f"**{src}** — {len(df):,} registros, {df.shape[1]} colunas")
                st.dataframe(df.head(8), use_container_width=True)
    else:
        section_header("📥", "Passo 2 — Baixar Dados")
        st.caption(f"Fontes necessárias para este desfecho: **{', '.join(outcome.data_sources)}**")

        c1, c2 = st.columns(2)
        with c1:
            ss["sel_states"] = st.multiselect(
                "Estados (UF)", STATES, default=ss["sel_states"], key="inp_states"
            )
        with c2:
            ss["sel_years"] = st.multiselect(
                "Anos", list(range(2018, 2025)), default=ss["sel_years"], key="inp_years"
            )

        if not ss["sel_states"] or not ss["sel_years"]:
            st.info("Selecione pelo menos um estado e um ano para continuar.")
            st.stop()

        if st.button("⬇️ Baixar Dados do DataSUS", type="primary", use_container_width=True):
            raw_data: dict = {}
            manual_needed: list = []

            for source in outcome.data_sources:
                prog = st.progress(0.0, text=f"Baixando {source}…")
                try:
                    dfs = []
                    for state in ss["sel_states"]:
                        for year in ss["sel_years"]:
                            dfs.append(
                                fetch(
                                    source, state, year,
                                    lambda p, m, _p=prog: _p.progress(min(p, 1.0), text=m),
                                )
                            )
                    df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
                    raw_data[source] = df
                    prog.progress(1.0, text=f"✅ {source}: {len(df):,} registros")
                except ManualUploadRequired as e:
                    prog.empty()
                    manual_needed.append((source, str(e)))
                except Exception as e:
                    prog.empty()
                    st.error(f"Erro ao baixar {source}: {e}")

            ss["raw_data"] = raw_data
            ss["cohort"] = None
            ss["model_results"] = None
            ss["manual_needed"] = manual_needed

            if raw_data and not manual_needed:
                st.rerun()

        # Upload manual (fallback)
        if ss["manual_needed"]:
            st.warning(
                "⚠️ Download automático indisponível para algumas fontes. "
                "Faça o upload manual dos CSVs abaixo."
            )
            raw_data = ss.get("raw_data", {})
            for source, msg in ss["manual_needed"]:
                with st.expander(f"Upload: {source}", expanded=True):
                    st.caption(msg)
                    uploaded = st.file_uploader(
                        f"CSV do {source}", type=["csv", "txt"], key=f"up_{source}"
                    )
                    if uploaded:
                        try:
                            state0 = ss["sel_states"][0] if len(ss["sel_states"]) == 1 else "BR"
                            year0 = ss["sel_years"][0] if len(ss["sel_years"]) == 1 else 0
                            df = load_from_csv(uploaded.read(), source, state0, year0)
                            raw_data[source] = df
                            ss["raw_data"] = raw_data
                            ss["cohort"] = None
                            st.success(f"✅ {source}: {len(df):,} registros carregados.")
                        except Exception as e:
                            st.error(f"Erro ao processar CSV: {e}")

            if set(outcome.data_sources) <= set(raw_data.keys()):
                ss["manual_needed"] = []
                st.rerun()

        st.stop()

st.markdown('<hr style="margin:16px 0">', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 3 — COORTE
# ═════════════════════════════════════════════════════════════════════════════
with st.container():
    if ss["cohort"] is not None:
        cohort = ss["cohort"]
        builder = CohortBuilder(outcome)
        bal = builder.class_balance(cohort)
        compact_row(
            "🔬 Coorte:",
            f"**{bal['total']:,}** registros — prevalência **{bal['prevalence']:.1%}**",
            "chg_cohort",
            ["cohort", "model_results"],
        )
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", f"{bal['total']:,}")
        c2.metric("Positivos", f"{bal['positive']:,}")
        c3.metric("Negativos", f"{bal['negative']:,}")
        c4.metric("Prevalência", f"{bal['prevalence']:.1%}")

        with st.expander("Distribuição e dados faltantes"):
            col_a, col_b = st.columns(2)
            with col_a:
                fig_pie = px.pie(
                    values=[bal["positive"], bal["negative"]],
                    names=["Positivo (1)", "Negativo (0)"],
                    color_discrete_sequence=["#ef4444", "#3b82f6"],
                    title="Distribuição do Desfecho",
                )
                fig_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=280)
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_b:
                missing = (cohort.isnull().mean() * 100).sort_values(ascending=False)
                missing = missing[missing > 0].head(15)
                if not missing.empty:
                    fig_miss = px.bar(
                        x=missing.values,
                        y=missing.index,
                        orientation="h",
                        labels={"x": "% faltante", "y": ""},
                        title="Dados faltantes por coluna",
                        color=missing.values,
                        color_continuous_scale="Reds",
                    )
                    fig_miss.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=280, showlegend=False)
                    st.plotly_chart(fig_miss, use_container_width=True)
                else:
                    st.success("Sem dados faltantes nas colunas selecionadas.")
            st.dataframe(cohort.head(50), use_container_width=True)
    else:
        section_header("🔬", "Passo 3 — Construir Coorte")
        st.caption(
            "Processa os dados brutos: filtra casos elegíveis, cria features e define o target."
        )
        if st.button("🔨 Construir Coorte", type="primary", use_container_width=True):
            with st.spinner("Construindo coorte… isso pode levar alguns minutos."):
                try:
                    builder = CohortBuilder(outcome)
                    cohort = builder.build(ss["raw_data"])
                    ss["cohort"] = cohort
                    ss["model_results"] = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao construir coorte: {e}")
                    st.exception(e)
        st.stop()

st.markdown('<hr style="margin:16px 0">', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 4 — MODELO
# ═════════════════════════════════════════════════════════════════════════════
cohort = ss["cohort"]
builder = CohortBuilder(outcome)
X, y = builder.get_Xy(cohort)

with st.container():
    if ss["model_results"]:
        results = ss["model_results"]
        m = results["mean_metrics"]
        compact_row(
            "🤖 Modelo:",
            f"**{results['algorithm'].upper()}** — "
            f"AUC {m['roc_auc']:.3f} | F1 {m['f1']:.3f} | PR-AUC {m['pr_auc']:.3f}",
            "chg_model",
            ["model_results"],
        )
    else:
        section_header("🤖", "Passo 4 — Treinar Modelo")
        bal = builder.class_balance(cohort)
        st.info(
            f"Cohort pronto: **{bal['total']:,}** registros | "
            f"Prevalência: **{bal['prevalence']:.1%}** | "
            f"Features disponíveis: **{len(X.columns)}**"
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Algoritmo e validação**")
            algo_label = st.selectbox("Algoritmo", list(ALGORITHMS.keys()), key="algo_sel")
            algo = ALGORITHMS[algo_label]
            n_folds = st.slider("Folds (cross-validation)", 3, 10, 5, key="cv_folds")
            use_smote = st.checkbox(
                "SMOTE — oversample da classe minoritária",
                help="Recomendado quando prevalência < 5%",
                key="use_smote",
            )
        with c2:
            st.markdown("**Hiperparâmetros**")
            params: dict = {}
            if algo in ("lgbm", "xgb", "rf"):
                params["n_estimators"] = st.slider("Árvores (n_estimators)", 50, 1000, 300, 50, key="n_est")
            if algo in ("lgbm", "xgb"):
                params["learning_rate"] = st.select_slider(
                    "Learning rate",
                    options=[0.005, 0.01, 0.02, 0.05, 0.1, 0.2],
                    value=0.05,
                    key="lr",
                )
            if algo in ("lgbm", "xgb", "rf"):
                params["max_depth"] = st.slider("max_depth (−1 = sem limite)", -1, 15, -1, key="mdepth")
            if algo == "logreg":
                params["C"] = st.select_slider(
                    "C (regularização)", [0.001, 0.01, 0.1, 1.0, 10.0], value=1.0, key="c_reg"
                )

        feat_cols = X.columns.tolist()
        selected_features = st.multiselect(
            "Features para o modelo",
            feat_cols,
            default=feat_cols,
            key="feat_sel",
            help="Por padrão todas as features sugeridas são incluídas.",
        )

        if not selected_features:
            st.warning("Selecione pelo menos uma feature.")
            st.stop()

        if st.button(
            f"🚀 Treinar {algo_label} com {n_folds}-fold CV",
            type="primary",
            use_container_width=True,
            key="train_btn",
        ):
            with st.spinner(f"Treinando {algo_label}…"):
                try:
                    results = train_cv(
                        X=X[selected_features],
                        y=y,
                        algorithm=algo,
                        params=params,
                        n_folds=n_folds,
                        use_smote=use_smote,
                    )
                    ss["model_results"] = results
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro no treino: {e}")
                    st.exception(e)
        st.stop()

st.markdown('<hr style="margin:16px 0">', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# ETAPA 5 — RESULTADOS
# ═════════════════════════════════════════════════════════════════════════════
results = ss["model_results"]
section_header("📊", "Resultados", done=False)

m = results["mean_metrics"]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("ROC-AUC", f"{m['roc_auc']:.4f}")
c2.metric("PR-AUC", f"{m['pr_auc']:.4f}")
c3.metric("F1-Score", f"{m['f1']:.4f}")
c4.metric("Recall", f"{m['recall']:.4f}")
c5.metric("Brier Score", f"{m['brier']:.4f}")

with st.expander("Métricas por fold"):
    st.dataframe(ev.fold_metrics_table(results["fold_metrics"]), use_container_width=True)

st.markdown("#### Curvas de desempenho")
X_res = X[results["X_columns"]]
oof = results["oof_probs"]
y_arr = y.values

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(ev.roc_chart(y_arr, oof), use_container_width=True)
with col2:
    st.plotly_chart(ev.pr_chart(y_arr, oof), use_container_width=True)

st.plotly_chart(ev.calibration_chart(y_arr, oof), use_container_width=False)

st.markdown("#### Distribuição dos scores preditos")
fig_dist = px.histogram(
    x=oof,
    color=y_arr.astype(str),
    nbins=50,
    barmode="overlay",
    opacity=0.65,
    labels={"x": "Score predito", "color": "Desfecho real"},
    color_discrete_map={"0": "#3b82f6", "1": "#ef4444"},
    title="Scores por classe real",
)
fig_dist.update_layout(margin=dict(t=40, b=0))
st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("#### Importância das variáveis")
if results.get("feature_importances"):
    st.plotly_chart(ev.importance_chart(results["feature_importances"]), use_container_width=False)

st.markdown("#### SHAP — Explicabilidade")
with st.spinner("Calculando SHAP…"):
    shap_fig = ev.shap_summary(results["model"], X_res.head(500))
if shap_fig:
    st.plotly_chart(shap_fig, use_container_width=False)
else:
    st.info("SHAP indisponível para este algoritmo. Instale: `pip install shap`")

st.markdown("#### Exportar predições")
export_df = pd.DataFrame({
    "score": oof,
    "predicao": (oof >= 0.5).astype(int),
    "real": y_arr,
})
st.download_button(
    label="⬇️ Baixar predições OOF (CSV)",
    data=export_df.to_csv(index=False).encode("utf-8"),
    file_name=f"predicoes_{ss['outcome_key']}.csv",
    mime="text/csv",
)
