"""Evaluation metrics and plotly chart builders for the Results page."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_curve, precision_recall_curve


def roc_chart(y_true: np.ndarray, oof_probs: np.ndarray) -> go.Figure:
    fpr, tpr, _ = roc_curve(y_true, oof_probs)
    auc = np.trapz(tpr, fpr)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"ROC (AUC={auc:.3f})", line=dict(color="#1f77b4", width=2)))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random", line=dict(dash="dash", color="gray")))
    fig.update_layout(
        title="Curva ROC (OOF)",
        xaxis_title="Taxa de Falsos Positivos",
        yaxis_title="Taxa de Verdadeiros Positivos",
        width=550, height=420,
    )
    return fig


def pr_chart(y_true: np.ndarray, oof_probs: np.ndarray) -> go.Figure:
    precision, recall, _ = precision_recall_curve(y_true, oof_probs)
    auc = np.trapz(precision, recall[::-1])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=recall, y=precision, mode="lines", name=f"PR (AUC={auc:.3f})", line=dict(color="#ff7f0e", width=2)))
    prevalence = y_true.mean()
    fig.add_hline(y=prevalence, line_dash="dash", line_color="gray", annotation_text=f"Baseline ({prevalence:.2%})")
    fig.update_layout(
        title="Curva Precision-Recall (OOF)",
        xaxis_title="Recall",
        yaxis_title="Precision",
        width=550, height=420,
    )
    return fig


def calibration_chart(y_true: np.ndarray, oof_probs: np.ndarray, n_bins: int = 10) -> go.Figure:
    prob_true, prob_pred = calibration_curve(y_true, oof_probs, n_bins=n_bins, strategy="uniform")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prob_pred, y=prob_true, mode="lines+markers", name="Modelo", line=dict(color="#2ca02c", width=2)))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Calibração perfeita", line=dict(dash="dash", color="gray")))
    fig.update_layout(
        title="Curva de Calibração",
        xaxis_title="Probabilidade prevista",
        yaxis_title="Fração de positivos reais",
        width=550, height=420,
    )
    return fig


def importance_chart(feature_importances: dict, top_n: int = 20) -> go.Figure:
    df = pd.Series(feature_importances).sort_values(ascending=True).tail(top_n)
    fig = go.Figure(go.Bar(x=df.values, y=df.index, orientation="h", marker_color="#1f77b4"))
    fig.update_layout(
        title=f"Top {top_n} Variáveis por Importância",
        xaxis_title="Importância",
        height=max(300, top_n * 22),
        width=600,
        margin=dict(l=180),
    )
    return fig


def shap_summary(model, X: pd.DataFrame, max_display: int = 20) -> go.Figure | None:
    """Compute SHAP values and return a summary bar chart (Plotly)."""
    try:
        import shap
    except ImportError:
        return None

    # Get the underlying estimator (last step)
    estimator = model[-1]
    prep = model[:-1]
    X_transformed = prep.transform(X)
    if hasattr(X_transformed, "toarray"):
        X_transformed = X_transformed.toarray()

    col_names = X.columns.tolist()
    X_t = pd.DataFrame(X_transformed, columns=col_names[:X_transformed.shape[1]])

    try:
        explainer = shap.TreeExplainer(estimator)
        shap_values = explainer.shap_values(X_t)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
    except Exception:
        try:
            explainer = shap.LinearExplainer(estimator, X_t)
            shap_values = explainer.shap_values(X_t)
        except Exception:
            return None

    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    idx = np.argsort(mean_abs_shap)[-max_display:]
    df = pd.DataFrame({"feature": np.array(col_names[:len(mean_abs_shap)])[idx], "shap": mean_abs_shap[idx]})
    fig = go.Figure(go.Bar(x=df["shap"], y=df["feature"], orientation="h", marker_color="#d62728"))
    fig.update_layout(
        title=f"SHAP — Importância média absoluta (top {max_display})",
        xaxis_title="|SHAP value|",
        height=max(300, max_display * 22),
        width=620,
        margin=dict(l=180),
    )
    return fig


def calibration_comparison_chart(
    y_true: np.ndarray,
    probs_before: np.ndarray,
    probs_after: np.ndarray,
    method_label: str = "Calibrado",
    n_bins: int = 10,
) -> go.Figure:
    """Show before/after calibration curves on the same plot."""
    pb_true, pb_pred = calibration_curve(y_true, probs_before, n_bins=n_bins, strategy="uniform")
    pa_true, pa_pred = calibration_curve(y_true, probs_after, n_bins=n_bins, strategy="uniform")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pb_pred, y=pb_true, mode="lines+markers", name="Antes da calibração",
        line=dict(color="#94a3b8", width=2, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=pa_pred, y=pa_true, mode="lines+markers", name=method_label,
        line=dict(color="#1a56db", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines", name="Perfeito",
        line=dict(dash="dash", color="#059669"),
    ))
    fig.update_layout(
        title="Curva de Calibração — antes e depois",
        xaxis_title="Probabilidade prevista",
        yaxis_title="Fração de positivos reais",
        width=600, height=420,
    )
    return fig


def shap_comparison_chart(
    shap_dicts: list[dict],
    labels: list[str],
    top_n: int = 15,
) -> go.Figure:
    """Grouped bar chart comparing mean |SHAP| per feature across multiple cohorts."""
    # Union of top features across all groups
    all_features: dict[str, float] = {}
    for d in shap_dicts:
        for feat, val in d.items():
            all_features[feat] = all_features.get(feat, 0) + val
    top_features = sorted(all_features, key=all_features.get, reverse=True)[:top_n]

    palette = ["#1a56db", "#059669", "#d97706", "#e11d48", "#7c3aed", "#0891b2"]
    fig = go.Figure()
    for i, (label, shap_d) in enumerate(zip(labels, shap_dicts)):
        vals = [shap_d.get(f, 0.0) for f in top_features]
        fig.add_trace(go.Bar(
            name=label,
            x=vals,
            y=top_features,
            orientation="h",
            marker_color=palette[i % len(palette)],
        ))
    fig.update_layout(
        barmode="group",
        title=f"Comparação SHAP — top {top_n} variáveis",
        xaxis_title="|SHAP value| médio",
        height=max(350, top_n * 28),
        width=720,
        margin=dict(l=160),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def metrics_comparison_table(comparison_results: list[dict]) -> pd.DataFrame:
    """Build a DataFrame from a list of {label, metrics, n} dicts."""
    rows = []
    for r in comparison_results:
        m = r["metrics"]
        rows.append({
            "Coorte": r["label"],
            "N": f"{r['n']:,}",
            "ROC-AUC": round(m.get("roc_auc", float("nan")), 4),
            "PR-AUC": round(m.get("pr_auc", float("nan")), 4),
            "F1": round(m.get("f1", float("nan")), 4),
            "Recall": round(m.get("recall", float("nan")), 4),
            "Brier": round(m.get("brier", float("nan")), 4),
        })
    return pd.DataFrame(rows)


def shap_values_dict(model, X: pd.DataFrame, max_rows: int = 500) -> dict:
    """Return {feature: mean_abs_shap} using TreeExplainer or LinearExplainer."""
    try:
        import shap
    except ImportError:
        return {}

    estimator = model[-1]
    prep = model[:-1]
    X_sub = X.head(max_rows)
    X_transformed = prep.transform(X_sub)
    if hasattr(X_transformed, "toarray"):
        X_transformed = X_transformed.toarray()
    col_names = X_sub.columns.tolist()
    X_t = pd.DataFrame(X_transformed, columns=col_names[: X_transformed.shape[1]])

    try:
        explainer = shap.TreeExplainer(estimator)
        sv = explainer.shap_values(X_t)
        if isinstance(sv, list):
            sv = sv[1]
    except Exception:
        try:
            explainer = shap.LinearExplainer(estimator, X_t)
            sv = explainer.shap_values(X_t)
        except Exception:
            return {}

    mean_abs = np.abs(sv).mean(axis=0)
    n = min(len(col_names), len(mean_abs))
    return dict(zip(col_names[:n], mean_abs[:n].tolist()))


def fold_metrics_table(fold_metrics: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(fold_metrics)
    df = df.rename(columns={"roc_auc": "ROC-AUC", "pr_auc": "PR-AUC", "f1": "F1", "precision": "Precisão", "recall": "Recall", "brier": "Brier", "fold": "Fold"})
    numeric = [c for c in df.columns if c != "Fold"]
    df[numeric] = df[numeric].round(4)
    return df
