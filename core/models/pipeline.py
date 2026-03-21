"""ML training pipeline with cross-validation.

Supported algorithms: LightGBM (default), XGBoost, Logistic Regression, Random Forest.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, average_precision_score, f1_score,
    precision_score, recall_score, brier_score_loss,
)


ALGORITHMS = {
    "LightGBM": "lgbm",
    "XGBoost": "xgb",
    "Logistic Regression": "logreg",
    "Random Forest": "rf",
}


def _build_model(algorithm: str, params: dict):
    if algorithm == "lgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(
            n_estimators=params.get("n_estimators", 300),
            learning_rate=params.get("learning_rate", 0.05),
            max_depth=params.get("max_depth", -1),
            num_leaves=params.get("num_leaves", 31),
            class_weight="balanced",
            random_state=42,
            verbose=-1,
        )
    if algorithm == "xgb":
        from xgboost import XGBClassifier
        return XGBClassifier(
            n_estimators=params.get("n_estimators", 300),
            learning_rate=params.get("learning_rate", 0.05),
            max_depth=params.get("max_depth", 6),
            scale_pos_weight=params.get("scale_pos_weight", 1),
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
        )
    if algorithm == "logreg":
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression(
            C=params.get("C", 1.0),
            class_weight="balanced",
            max_iter=1000,
            random_state=42,
        )
    if algorithm == "rf":
        from sklearn.ensemble import RandomForestClassifier
        return RandomForestClassifier(
            n_estimators=params.get("n_estimators", 200),
            max_depth=params.get("max_depth", None),
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
    raise ValueError(f"Unknown algorithm: {algorithm}")


def build_pipeline(
    X: pd.DataFrame,
    algorithm: str = "lgbm",
    params: dict | None = None,
    use_smote: bool = False,
) -> Pipeline:
    """Build a full sklearn Pipeline with imputation + optional scaling + model."""
    params = params or {}
    num_cols = X.select_dtypes(include="number").columns.tolist()

    preprocessor = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), num_cols),
    ], remainder="drop")

    steps = [("prep", preprocessor)]

    if algorithm == "logreg":
        steps.append(("scaler", StandardScaler()))

    if use_smote:
        try:
            from imblearn.over_sampling import SMOTE
            from imblearn.pipeline import Pipeline as ImbPipeline
            steps.append(("smote", SMOTE(random_state=42)))
            steps.append(("model", _build_model(algorithm, params)))
            return ImbPipeline(steps)
        except ImportError:
            pass  # fall through to standard pipeline

    steps.append(("model", _build_model(algorithm, params)))
    return Pipeline(steps)


def train_cv(
    X: pd.DataFrame,
    y: pd.Series,
    algorithm: str = "lgbm",
    params: dict | None = None,
    n_folds: int = 5,
    use_smote: bool = False,
) -> dict:
    """Train with StratifiedKFold CV and return per-fold + aggregate metrics.

    Returns:
        dict with keys:
            fold_metrics: list of per-fold metric dicts
            mean_metrics: averaged across folds
            oof_probs: out-of-fold predicted probabilities (N,)
            feature_importances: dict col→importance (tree models only)
            model: fitted pipeline on full data
    """
    params = params or {}
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

    oof_probs = np.zeros(len(y))
    fold_metrics = []
    importances_list = []

    for fold, (tr_idx, vl_idx) in enumerate(skf.split(X, y)):
        X_tr, X_vl = X.iloc[tr_idx], X.iloc[vl_idx]
        y_tr, y_vl = y.iloc[tr_idx], y.iloc[vl_idx]

        pipe = build_pipeline(X_tr, algorithm, params, use_smote)
        pipe.fit(X_tr, y_tr)

        probs = pipe.predict_proba(X_vl)[:, 1]
        preds = (probs >= 0.5).astype(int)
        oof_probs[vl_idx] = probs

        metrics = _compute_metrics(y_vl, probs, preds)
        metrics["fold"] = fold + 1
        fold_metrics.append(metrics)

        # Feature importance (tree models)
        imp = _get_importances(pipe, X.columns.tolist())
        if imp is not None:
            importances_list.append(imp)

    # Mean across folds
    mean_metrics = {
        k: float(np.mean([f[k] for f in fold_metrics]))
        for k in fold_metrics[0] if k != "fold"
    }

    # Average feature importances
    feature_importances = {}
    if importances_list:
        all_imp = pd.DataFrame(importances_list)
        feature_importances = all_imp.mean().to_dict()

    # Refit on full data
    final_pipe = build_pipeline(X, algorithm, params, use_smote)
    final_pipe.fit(X, y)

    return {
        "fold_metrics": fold_metrics,
        "mean_metrics": mean_metrics,
        "oof_probs": oof_probs,
        "feature_importances": feature_importances,
        "model": final_pipe,
        "X_columns": X.columns.tolist(),
        "algorithm": algorithm,
    }


def _compute_metrics(y_true, probs, preds) -> dict:
    return {
        "roc_auc": roc_auc_score(y_true, probs),
        "pr_auc": average_precision_score(y_true, probs),
        "f1": f1_score(y_true, preds, zero_division=0),
        "precision": precision_score(y_true, preds, zero_division=0),
        "recall": recall_score(y_true, preds, zero_division=0),
        "brier": brier_score_loss(y_true, probs),
    }


def _get_importances(pipe: Pipeline, feature_names: list[str]) -> dict | None:
    model = pipe[-1]
    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_
        if len(imp) == len(feature_names):
            return dict(zip(feature_names, imp))
    elif hasattr(model, "coef_"):
        imp = np.abs(model.coef_[0])
        if len(imp) == len(feature_names):
            return dict(zip(feature_names, imp))
    return None
