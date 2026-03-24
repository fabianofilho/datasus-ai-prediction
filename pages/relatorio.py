"""DataSUS AI Prediction — Relatório exportável (passo 10)."""
from __future__ import annotations
from pathlib import Path
from PIL import Image as _PILImage

import streamlit as st
from core.outcomes import OUTCOMES


@st.cache_resource(show_spinner=False)
def _pd():
    import pandas as pd
    return pd


@st.cache_resource(show_spinner=False)
def _ev():
    from core.models import evaluation
    return evaluation


_favicon = _PILImage.open(Path(__file__).parent.parent / "favicon.png")
st.set_page_config(
    page_title="Relatório — DataSUS AI",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS + topbar (shared design system) ───────────────────────────────────────
st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,300,0,0" />

<style>
:root {
  --primary: #111827; --primary-hover: #374151;
  --primary-light: #f3f4f6; --primary-ring: rgba(17,24,39,.12);
  --bg: #ffffff; --bg-page: #ffffff;
  --fg: #111827; --muted: #6b7280; --border: #e5e7eb;
  --done-bg: #f9fafb; --done-border: #e5e7eb; --done-fg: #374151;
  --radius: 6px; --topbar-h: 52px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,.05);
}
.ms {
  font-family: 'Material Symbols Outlined';
  font-style: normal; font-weight: normal;
  font-size: 1rem; line-height: 1;
  vertical-align: middle; display: inline-block;
  color: var(--fg);
}
header, footer,
[data-testid="stSidebarNav"], [data-testid="stHeader"],
[data-testid="stToolbar"], [data-testid="stDecoration"],
#MainMenu { display: none !important; }

html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif !important;
  color: var(--fg) !important;
}
.block-container {
  padding-top: calc(var(--topbar-h) + 32px) !important;
  padding-bottom: 56px !important;
  padding-left: 40px !important; padding-right: 40px !important;
  max-width: 1100px !important;
}
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {
  position: fixed !important;
  top: 0 !important; left: 0 !important;
  height: var(--topbar-h) !important; width: 52px !important;
  z-index: 10001 !important;
  background: #ffffff !important; border: none !important;
  border-right: 1px solid #e5e7eb !important;
  display: flex !important; align-items: center !important;
  justify-content: center !important; cursor: pointer !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg {
  color: #111827 !important; fill: #111827 !important;
  width: 18px !important; height: 18px !important;
}
[data-testid="stSidebar"] {
  top: var(--topbar-h) !important;
  height: calc(100vh - var(--topbar-h)) !important;
  background: #ffffff !important; border-right: 1px solid #e5e7eb !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 1.25rem 1rem 1rem !important;
  height: 100% !important; overflow-y: auto !important;
}
.ds-topbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  height: var(--topbar-h); background: var(--bg);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 48px 0 calc(52px + 20px);
}
.ds-topbar-logo {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.93rem; font-weight: 700;
  color: #111827 !important; text-decoration: none !important;
}
.ds-topbar-badge {
  background: var(--fg); color: #fff;
  font-size: 0.62rem; font-weight: 700;
  padding: 2px 7px; border-radius: 4px; letter-spacing: .06em;
}
.ds-topbar-right {
  font-size: 0.78rem; color: #111827; font-weight: 500;
  text-decoration: none !important;
  display: flex; align-items: center; gap: 5px;
}
.ds-topbar-right:hover { opacity: 0.7; }
.ds-stepbar {
  display: flex; align-items: center; gap: 2px; flex-wrap: nowrap;
  overflow-x: auto; scrollbar-width: none;
  margin-bottom: 28px; padding: 10px 0; border-bottom: 1px solid var(--border);
}
.ds-stepbar::-webkit-scrollbar { display: none; }
.ds-step {
  border-radius: 4px; padding: 2px 7px;
  font-size: 0.7rem; font-weight: 500; white-space: nowrap; flex-shrink: 0;
}
.ds-step-done   { color: var(--muted); }
.ds-step-active { background: var(--fg); color: #fff; font-weight: 600; }
.ds-step-locked { color: #d1d5db; }
.ds-step-optional { color: #d1d5db; }
.ds-step-arrow  { color: #d1d5db; font-size: 0.75rem; padding: 0; flex-shrink: 0; }
.ds-done-bar {
  background: var(--done-bg); border: 1px solid var(--done-border);
  border-radius: var(--radius); padding: 9px 14px; margin-bottom: 4px;
}
.ds-done-label { font-size: 0.84rem; color: var(--done-fg); }
.ds-section-title { font-size: 1rem; font-weight: 700; color: var(--fg); margin: 0 0 3px; }
.ds-section-caption { font-size: 0.8rem; color: var(--muted); margin: 0 0 16px; }
.ds-divider { border: none; border-top: 1px solid var(--border); margin: 20px 0; }
[data-testid="stMetric"] {
  background: var(--bg) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; padding: 14px 18px !important;
  box-shadow: none !important;
}
.stButton { display: flex !important; justify-content: flex-start !important; }
.stButton > button {
  width: auto !important; min-width: 0 !important; padding: 5px 16px !important;
  border-radius: var(--radius) !important; font-size: 0.82rem !important;
  font-weight: 500 !important; transition: all .12s !important;
  cursor: pointer !important; white-space: nowrap !important;
}
.stButton > button[kind="primary"] {
  background: var(--fg) !important; border: 1px solid var(--fg) !important;
  color: #fff !important; font-weight: 600 !important; box-shadow: none !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--primary-hover) !important; border-color: var(--primary-hover) !important;
}
.stButton > button[kind="secondary"] {
  background: #fff !important; border: 1px solid var(--border) !important;
  color: var(--fg) !important; box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: var(--fg) !important; background: var(--primary-light) !important;
}
[data-testid="stInfo"], [data-testid="stWarning"],
[data-testid="stSuccess"] { border-radius: var(--radius) !important; }
.ds-info-box {
  background: #f9fafb !important; border: 1px solid #e5e7eb !important;
  border-radius: var(--radius) !important; padding: 12px 16px !important;
  margin: 4px 0 12px !important; font-size: 0.85rem !important;
  color: #374151 !important; line-height: 1.5 !important;
}
.ds-info-box * { color: #374151 !important; }
.ds-warn-box {
  background: #f9fafb !important; border: 1px solid #e5e7eb !important;
  border-left: 3px solid #d1d5db !important; border-radius: var(--radius) !important;
  padding: 12px 16px !important; margin: 4px 0 12px !important;
  font-size: 0.85rem !important; color: #374151 !important; line-height: 1.5 !important;
}
.ds-warn-box * { color: #374151 !important; }
[data-testid="stExpander"] {
  background: var(--bg) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; box-shadow: none !important;
}
.ds-page { display: contents; }
.sb-title {
  font-size: .65rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .1em; color: #6b7280; margin-bottom: 10px;
  padding-bottom: 6px; border-bottom: 1px solid #e5e7eb;
}
.sb-step {
  padding: 8px 10px; margin-bottom: 5px;
  border: 1px solid #e5e7eb; border-radius: 6px; background: #f9fafb;
}
.sb-step-label {
  font-size: .6rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .08em; color: #6b7280; margin-bottom: 2px;
}
.sb-step-value { font-size: .78rem; color: #111827; font-weight: 500; line-height: 1.35; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
ss = st.session_state


# ── Helpers ───────────────────────────────────────────────────────────────────

def render_topbar() -> None:
    st.markdown(
        '<div class="ds-topbar">'
        '<a class="ds-topbar-logo" href="/" target="_self">'
        '<span class="ms" style="font-size:1.2rem;color:#111827">local_hospital</span>'
        'DataSUS AI'
        '<span class="ds-topbar-badge">PREDICTION</span>'
        '</a>'
        '<a class="ds-topbar-right" href="/" target="_self">'
        '<span class="ms">summarize</span>Relatório Final'
        '</a>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_step_bar() -> None:
    labels = ["Desfecho", "Dados", "Features", "Tratamento", "Modelo",
              "Treinamento", "Resultados", "Benchmark", "Deploy", "Relatório"]
    optionals = {8, 9, 10}
    parts = []
    for i, lbl in enumerate(labels, 1):
        optional = i in optionals
        if i < 10:
            cls = "ds-step ds-step-done"
            dot = "✓"
        elif i == 10:
            cls = "ds-step ds-step-active"
            dot = "10"
        else:
            cls = "ds-step ds-step-optional"
            dot = str(i)
        suffix = " *" if optional else ""
        parts.append(f'<span class="{cls}">{dot}. {lbl}{suffix}</span>')
        if i < len(labels):
            parts.append('<span class="ds-step-arrow">›</span>')
    st.markdown(
        '<div class="ds-stepbar">'
        + "".join(parts)
        + '<span style="margin-left:auto;font-size:0.65rem;color:#9ca3af;'
        + 'white-space:nowrap;flex-shrink:0;">* etapa opcional</span>'
        + "</div>",
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown('<p class="sb-title">Pipeline</p>', unsafe_allow_html=True)
        if ss.get("outcome_key"):
            o = OUTCOMES[ss["outcome_key"]]
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">1 · Desfecho</div>'
                f'<div class="sb-step-value">{o.name}<br>'
                f'<span style="font-size:.7rem;color:#6b7280">{", ".join(o.data_sources)}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        if ss.get("raw_data"):
            _lines = "<br>".join(f"{src}: {len(df):,}" for src, df in ss["raw_data"].items())
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">2 · Dados</div>'
                f'<div class="sb-step-value">{_lines}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        if ss.get("model_results"):
            r_ = ss["model_results"]
            m_ = r_["mean_metrics"]
            st.markdown(
                f'<div class="sb-step">'
                f'<div class="sb-step-label">7 · Modelo</div>'
                f'<div class="sb-step-value">'
                f'AUC {m_["roc_auc"]:.3f}<br>'
                f'<span style="font-size:.7rem;color:var(--muted)">{r_.get("algo_label","")}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )


def step_title(n: int, title: str, caption: str = "") -> None:
    st.markdown(
        f'<p class="ds-section-title">Passo {n} — {title}</p>'
        + (f'<p class="ds-section-caption">{caption}</p>' if caption else ""),
        unsafe_allow_html=True,
    )


def _build_html_report(outcome, results, m, calib, comp, fc, mc, ss_data: dict) -> str:
    import datetime
    algo = results.get("algo_label", "—")
    features = fc.get("selected_features", results.get("X_columns", []))
    states = ", ".join(ss_data.get("sel_states") or [])
    years = ", ".join(map(str, ss_data.get("sel_years") or []))
    ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    feat_list = "".join(f"<li><code>{f}</code></li>" for f in features)

    feat_imp_section = ""
    fi_data = results.get("feature_importances", {})
    if fi_data:
        top_fi = sorted(fi_data.items(), key=lambda x: x[1], reverse=True)[:15]
        fi_rows = "".join(
            f"<tr><td>{i+1}</td><td><code>{name}</code></td><td>{val:.4f}</td></tr>"
            for i, (name, val) in enumerate(top_fi)
        )
        feat_imp_section = f"""
        <h2>5. Importância de Features (Top 15)</h2>
        <table>
          <thead><tr><th>#</th><th>Feature</th><th>Importância</th></tr></thead>
          <tbody>{fi_rows}</tbody>
        </table>"""

    calib_section = ""
    if calib and not calib.get("skipped"):
        calib_section = f"""
        <h2>6. Calibração</h2>
        <table>
          <tr><th>Método</th><td>{calib.get('method','—').capitalize()}</td></tr>
          <tr><th>Brier antes</th><td>{calib.get('brier_before',0):.4f}</td></tr>
          <tr><th>Brier depois</th><td>{calib.get('brier_after',0):.4f}</td></tr>
          <tr><th>Variação</th><td>{calib.get('brier_delta',0):+.4f}</td></tr>
        </table>"""

    benchmark_section = ""
    if comp:
        rows = "".join(
            f"<tr><td>{r['label']}</td><td>{r['n']:,}</td>"
            f"<td>{r['metrics']['roc_auc']:.4f}</td><td>{r['metrics']['pr_auc']:.4f}</td>"
            f"<td>{r['metrics']['f1']:.4f}</td><td>{r['metrics']['brier']:.4f}</td></tr>"
            for r in comp
        )
        benchmark_section = f"""
        <h2>7. Benchmark entre Estados</h2>
        <table>
          <thead><tr><th>Coorte</th><th>N</th><th>ROC-AUC</th><th>PR-AUC</th><th>F1</th><th>Brier</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relatório DataSUS AI — {outcome.name}</title>
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;max-width:960px;margin:40px auto;color:#111827;padding:0 24px}}
  h1{{font-size:1.4rem;margin-bottom:4px}}
  h2{{font-size:1rem;font-weight:700;margin:28px 0 8px;border-bottom:1px solid #e5e7eb;padding-bottom:6px}}
  table{{border-collapse:collapse;width:100%;margin-bottom:12px}}
  th,td{{padding:8px 12px;border:1px solid #e5e7eb;font-size:.85rem}}
  th{{background:#f9fafb;font-weight:600;text-align:left}}
  .grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:16px}}
  .card{{border:1px solid #e5e7eb;border-radius:6px;padding:12px 16px}}
  .lbl{{font-size:.72rem;color:#6b7280;font-weight:500}}
  .val{{font-size:1.3rem;font-weight:700}}
  code{{background:#f3f4f6;padding:2px 5px;border-radius:3px;font-size:.82rem}}
  ul{{columns:3;padding-left:20px}}
  .footer{{margin-top:48px;font-size:.72rem;color:#9ca3af;text-align:center;border-top:1px solid #e5e7eb;padding-top:16px}}
</style>
</head>
<body>
<h1>Relatório — DataSUS AI Prediction</h1>
<p style="color:#6b7280;font-size:.85rem">Gerado em {ts} &nbsp;·&nbsp; {outcome.name}</p>

<h2>1. Desfecho e Dados</h2>
<table>
  <tr><th>Desfecho</th><td>{outcome.name}</td></tr>
  <tr><th>Descrição</th><td>{outcome.description}</td></tr>
  <tr><th>Fontes</th><td>{', '.join(outcome.data_sources)}</td></tr>
  <tr><th>Estados</th><td>{states}</td></tr>
  <tr><th>Anos</th><td>{years}</td></tr>
</table>

<h2>2. Modelo e Treinamento</h2>
<table>
  <tr><th>Algoritmo</th><td>{algo}</td></tr>
  <tr><th>Estratégia de validação</th><td>{mc.get('val_strategy','—')}</td></tr>
  <tr><th>Otimização HPO</th><td>{results.get('hpo_mode','Padrão')}</td></tr>
  <tr><th>Registros de treinamento</th><td>{results.get('sample_n',0):,}</td></tr>
</table>

<h2>3. Features Selecionadas ({len(features)})</h2>
<ul>{feat_list}</ul>

<h2>4. Métricas do Modelo</h2>
<div class="grid">
  <div class="card"><div class="lbl">ROC-AUC</div><div class="val">{m['roc_auc']:.4f}</div></div>
  <div class="card"><div class="lbl">Sensibilidade</div><div class="val">{m.get('recall',0):.4f}</div></div>
  <div class="card"><div class="lbl">Especificidade</div><div class="val">{m.get('specificity',0):.4f}</div></div>
  <div class="card"><div class="lbl">PR-AUC</div><div class="val">{m['pr_auc']:.4f}</div></div>
  <div class="card"><div class="lbl">F1-Score</div><div class="val">{m['f1']:.4f}</div></div>
</div>

{feat_imp_section}
{calib_section}
{benchmark_section}

<div class="footer">
  DataSUS AI Prediction &nbsp;·&nbsp; Análise independente baseada em dados públicos DATASUS<br>
  Não representa posicionamento oficial do Ministério da Saúde.
</div>
</body>
</html>"""


# ── Page rendering ─────────────────────────────────────────────────────────────
render_topbar()
render_sidebar()
st.markdown('<div class="ds-page">', unsafe_allow_html=True)

# ── Guard ──────────────────────────────────────────────────────────────────────
if not ss.get("model_results") or not ss.get("outcome_key"):
    st.warning("Nenhum modelo treinado encontrado. Complete o pipeline primeiro.")
    if st.button("← Voltar ao Pipeline", type="primary"):
        st.switch_page("pages/analise.py")
    st.stop()

if st.button("Resultados", icon=":material/arrow_back:", type="secondary"):
    st.switch_page("pages/analise.py")

render_step_bar()

pd = _pd()
ev = _ev()

outcome = OUTCOMES[ss["outcome_key"]]
results = ss["model_results"]
m = results["mean_metrics"]
calib = ss.get("calib_results") or {}
comp = ss.get("comparison_results") or []
fc = ss.get("feature_config") or {}
mc = ss.get("model_config") or {}

step_title(10, "Relatório do Modelo",
           "Resumo completo do pipeline — exportável para documentação e auditoria.")

import numpy as _np_rep

# ── 1. Desfecho e Dados ────────────────────────────────────────────────────────
st.markdown("### 1. Desfecho e Dados")
_d1, _d2 = st.columns(2)
with _d1:
    st.markdown(f"**Desfecho:** {outcome.name}")
    st.markdown(f"**Fontes:** {', '.join(outcome.data_sources)}")
    st.markdown(f"**Estados:** {', '.join(ss.get('sel_states') or [])}")
    st.markdown(f"**Anos:** {', '.join(map(str, ss.get('sel_years') or []))}")
with _d2:
    if ss.get("raw_data"):
        for _src, _df in ss["raw_data"].items():
            st.metric(f"Registros — {_src}", f"{len(_df):,}")
st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── 2. Features ────────────────────────────────────────────────────────────────
st.markdown("### 2. Features Selecionadas")
_feats = fc.get("selected_features", results.get("X_columns", []))
if _feats:
    _fcols = st.columns(4)
    for _fi, _fn in enumerate(_feats):
        _fcols[_fi % 4].markdown(f"`{_fn}`")
    st.caption(f"{len(_feats)} variável(is)")
st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── 3. Modelo e Treinamento ────────────────────────────────────────────────────
st.markdown("### 3. Modelo e Treinamento")
_m1, _m2 = st.columns(2)
with _m1:
    st.markdown(f"**Algoritmo:** {results.get('algo_label','—')}")
    st.markdown(f"**Validação:** {mc.get('val_strategy','—')}")
    st.markdown(f"**HPO:** {results.get('hpo_mode','Padrão')}")
    if results.get("sample_n"):
        st.markdown(f"**Registros:** {results['sample_n']:,}")
with _m2:
    _bp = results.get("best_params") or {}
    if _bp:
        with st.expander("Hiperparâmetros"):
            st.json(_bp)
st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── 4. Métricas ────────────────────────────────────────────────────────────────
st.markdown("### 4. Métricas do Modelo")
_mc1, _mc2, _mc3, _mc4, _mc5 = st.columns(5)
_mc1.metric("ROC-AUC",        f"{m['roc_auc']:.4f}")
_mc2.metric("Sensibilidade",  f"{m.get('recall',0):.4f}")
_mc3.metric("Especificidade", f"{m.get('specificity',0):.4f}")
_mc4.metric("PR-AUC",         f"{m['pr_auc']:.4f}")
_mc5.metric("F1-Score",       f"{m['f1']:.4f}")

_oof = results.get("oof_probs")
_y_eval = results.get("y_eval")
if _oof is not None and _y_eval is not None:
    import plotly.graph_objects as _go_rep
    _y_np  = _np_rep.array(_y_eval)
    _oof_np = _np_rep.array(_oof)

    # ── Curvas de desempenho ───────────────────────────────────────────────
    st.markdown("**Curvas de desempenho**")
    _col_roc, _col_pr = st.columns(2)
    with _col_roc:
        st.plotly_chart(ev.roc_chart(_y_np, _oof_np), use_container_width=True)
    with _col_pr:
        st.plotly_chart(ev.pr_chart(_y_np, _oof_np), use_container_width=True)

    # ── Distribuição dos scores preditos ──────────────────────────────────
    st.markdown("**Distribuição dos scores preditos**")
    _fig_dist = _go_rep.Figure()
    _fig_dist.add_trace(_go_rep.Histogram(
        x=_oof_np[_y_np == 0], name="Negativo (y=0)", nbinsx=40,
        marker_color="#3b82f6", opacity=0.7,
    ))
    _fig_dist.add_trace(_go_rep.Histogram(
        x=_oof_np[_y_np == 1], name="Positivo (y=1)", nbinsx=40,
        marker_color="#ef4444", opacity=0.7,
    ))
    _fig_dist.update_layout(
        barmode="overlay", xaxis_title="Score predito", yaxis_title="Frequência",
        height=300, margin=dict(t=20, b=40, l=40, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(_fig_dist, use_container_width=True)

    # ── Métricas Clínicas por Ponto de Corte ──────────────────────────────
    st.markdown("**Métricas Clínicas por Ponto de Corte**")
    st.plotly_chart(ev.threshold_curve_chart(_y_np, _oof_np), use_container_width=True)

    # ── Matriz de confusão (threshold 0.50) ───────────────────────────────
    st.markdown("**Matriz de confusão** (threshold 0.50)")
    _tm50 = ev.threshold_metrics(_y_np, _oof_np, 0.5)
    _cm_z50   = [[_tm50["tn"], _tm50["fp"]], [_tm50["fn"], _tm50["tp"]]]
    _cm_x50   = ["Pred Negativo", "Pred Positivo"]
    _cm_y50   = ["Real Negativo", "Real Positivo"]
    _cm_max50 = max(_tm50["tn"], _tm50["fp"], _tm50["fn"], _tm50["tp"]) or 1
    _cm_ann50 = []
    for _ri50, _row50 in enumerate(_cm_z50):
        for _ci50, _val50 in enumerate(_row50):
            _norm50 = _val50 / _cm_max50
            _cm_ann50.append(dict(
                x=_cm_x50[_ci50], y=_cm_y50[_ri50],
                text=f"<b>{_val50:,}</b>", showarrow=False,
                font=dict(size=16, color="white" if _norm50 > 0.45 else "#111827"),
                xref="x", yref="y",
            ))
    _cm_fig50 = _go_rep.Figure(_go_rep.Heatmap(
        z=_cm_z50, x=_cm_x50, y=_cm_y50,
        colorscale=[[0, "#f0fdf4"], [0.5, "#4ade80"], [1, "#166534"]],
        showscale=False,
    ))
    _cm_fig50.update_layout(
        height=300, margin=dict(t=20, b=40, l=110, r=20),
        xaxis=dict(side="bottom"),
        yaxis=dict(autorange="reversed", scaleanchor="x", scaleratio=1),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        annotations=_cm_ann50,
    )
    _cm_col50, _ = st.columns([1, 1])
    with _cm_col50:
        st.plotly_chart(_cm_fig50, use_container_width=True)

st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── 5. Importância de Features ─────────────────────────────────────────────────
_fi_rep = results.get("feature_importances", {})
if _fi_rep:
    st.markdown("### 5. Importância de Features")
    st.plotly_chart(ev.importance_chart(_fi_rep, top_n=20), use_container_width=True)
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── 6. Calibração ──────────────────────────────────────────────────────────────
if calib and not calib.get("skipped"):
    st.markdown("### 6. Calibração")
    _cal1, _cal2 = st.columns(2)
    with _cal1:
        st.plotly_chart(
            ev.calibration_comparison_chart(
                calib["y_eval"], calib["raw_probs"], calib["cal_probs"],
                method_label=f'Calibrado ({calib["method"]})',
            ),
            use_container_width=True,
        )
    with _cal2:
        st.metric("Brier antes", f"{calib['brier_before']:.4f}")
        st.metric("Brier depois", f"{calib['brier_after']:.4f}",
                  delta=f"{-calib['brier_delta']:+.4f}", delta_color="inverse")
        st.markdown(f"**Método:** {calib['method'].capitalize()}")
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── 7. Benchmark ───────────────────────────────────────────────────────────────
if comp:
    st.markdown("### 7. Benchmark entre Estados")
    st.dataframe(ev.metrics_comparison_table(comp), use_container_width=True, hide_index=True)
    _sdicts = [r["shap_dict"] for r in comp if r.get("shap_dict")]
    _slabels = [r["label"] for r in comp if r.get("shap_dict")]
    if len(_sdicts) >= 2:
        st.plotly_chart(ev.shap_comparison_chart(_sdicts, _slabels), use_container_width=True)
    st.markdown('<hr class="ds-divider">', unsafe_allow_html=True)

# ── Exportar ───────────────────────────────────────────────────────────────────
st.markdown("### Exportar Relatório HTML")
st.caption(
    "Gera um relatório HTML autocontido com todas as seções acima — "
    "adequado para compartilhar com gestores e equipes clínicas."
)
_html_report = _build_html_report(outcome, results, m, calib, comp, fc, mc, dict(ss))
st.download_button(
    label="Baixar relatório.html",
    data=_html_report,
    file_name=f"relatorio_{outcome.key}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.html",
    mime="text/html",
    use_container_width=False,
)

st.markdown('</div>', unsafe_allow_html=True)
