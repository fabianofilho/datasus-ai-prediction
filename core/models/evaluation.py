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


def fold_metrics_table(fold_metrics: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(fold_metrics)
    df = df.rename(columns={"roc_auc": "ROC-AUC", "pr_auc": "PR-AUC", "f1": "F1", "precision": "Precisão", "recall": "Recall", "brier": "Brier", "fold": "Fold"})
    numeric = [c for c in df.columns if c != "Fold"]
    df[numeric] = df[numeric].round(4)
    return df
