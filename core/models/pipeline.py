"""ML training pipeline with cross-validation and optional HPO.

Supported algorithms: LightGBM, XGBoost, Logistic Regression, Random Forest.
HPO modes: Manual, Random Search, Grid Search, Optuna.
Balancing: None, Class Weight, SMOTE (oversample), SMOTE + Undersampling.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold
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

# ── Param grids for Random Search (wide) ──────────────────────────────────────
_RANDOM_GRIDS: dict[str, dict] = {
    "lgbm": {
        "model__n_estimators":  [100, 200, 300, 500, 800],
        "model__learning_rate": [0.005, 0.01, 0.05, 0.1, 0.2],
        "model__max_depth":     [-1, 3, 5, 7, 10],
        "model__num_leaves":    [15, 31, 63, 100, 150],
    },
    "xgb": {
        "model__n_estimators":  [100, 200, 300, 500],
        "model__learning_rate": [0.005, 0.01, 0.05, 0.1, 0.2],
        "model__max_depth":     [3, 5, 7, 10],
    },
    "rf": {
        "model__n_estimators": [100, 200, 300, 500],
        "model__max_depth":    [None, 5, 10, 15, 20],
        "model__min_samples_split": [2, 5, 10],
    },
    "logreg": {
        "model__C": [0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
    },
}

# ── Param grids for Grid Search (focused) ────────────────────────────────────
_GRID_GRIDS: dict[str, dict] = {
    "lgbm": {
        "model__n_estimators":  [100, 300, 500],
        "model__learning_rate": [0.05, 0.1],
        "model__max_depth":     [-1, 5, 10],
    },
    "xgb": {
        "model__n_estimators":  [100, 300],
        "model__learning_rate": [0.05, 0.1],
        "model__max_depth":     [3, 6, 10],
    },
    "rf": {
        "model__n_estimators": [100, 200],
        "model__max_depth":    [None, 10, 20],
    },
    "logreg": {
        "model__C": [0.01, 0.1, 1.0, 10.0],
    },
}


def _build_model(algorithm: str, params: dict, class_weight: str | None = None):
    """Build a classifier. class_weight='balanced' or None."""
    if algorithm == "lgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(
            n_estimators=params.get("n_estimators", 300),
            learning_rate=params.get("learning_rate", 0.05),
            max_depth=params.get("max_depth", -1),
            num_leaves=params.get("num_leaves", 31),
            class_weight=class_weight,
            random_state=42,
            verbose=-1,
        )
    if algorithm == "xgb":
        from xgboost import XGBClassifier
        return XGBClassifier(
            n_estimators=params.get("n_estimators", 300),
            learning_rate=params.get("learning_rate", 0.05),
            max_depth=params.get("max_depth", 6),
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
        )
    if algorithm == "logreg":
        from sklearn.linear_model import LogisticRegression
        return LogisticRegression(
            C=params.get("C", 1.0),
            class_weight=class_weight,
            max_iter=1000,
            random_state=42,
        )
    if algorithm == "rf":
        from sklearn.ensemble import RandomForestClassifier
        return RandomForestClassifier(
            n_estimators=params.get("n_estimators", 200),
            max_depth=params.get("max_depth", None),
            min_samples_split=params.get("min_samples_split", 2),
            class_weight=class_weight,
            random_state=42,
            n_jobs=-1,
        )
    raise ValueError(f"Unknown algorithm: {algorithm}")


def _class_weight_for_balancing(balancing: str) -> str | None:
    """Return sklearn class_weight value given our balancing setting."""
    return "balanced" if balancing == "class_weight" else None


def build_pipeline(
    X: pd.DataFrame,
    algorithm: str = "lgbm",
    params: dict | None = None,
    use_smote: bool = False,         # kept for backward compat
    balancing: str = "none",         # "none"|"class_weight"|"smote_over"|"smote_under"
) -> Pipeline:
    """Build full sklearn/imblearn Pipeline with preprocessing + optional balancing."""
    params = params or {}
    num_cols = X.select_dtypes(include="number").columns.tolist()

    preprocessor = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), num_cols),
    ], remainder="drop")

    cw = _class_weight_for_balancing(balancing)
    steps: list = [("prep", preprocessor)]

    if algorithm == "logreg":
        steps.append(("scaler", StandardScaler()))

    # Resolve effective resampling
    do_smote_over  = balancing == "smote_over"  or use_smote
    do_smote_under = balancing == "smote_under"

    if do_smote_under or do_smote_over:
        try:
            from imblearn.pipeline import Pipeline as ImbPipeline
            if do_smote_under:
                try:
                    from imblearn.combine import SMOTETomek
                    steps.append(("resample", SMOTETomek(random_state=42)))
                except ImportError:
                    from imblearn.over_sampling import SMOTE
                    steps.append(("resample", SMOTE(random_state=42)))
            else:
                from imblearn.over_sampling import SMOTE
                steps.append(("resample", SMOTE(random_state=42)))
            steps.append(("model", _build_model(algorithm, params, cw)))
            return ImbPipeline(steps)
        except ImportError:
            pass  # fall through to standard pipeline

    steps.append(("model", _build_model(algorithm, params, cw)))
    return Pipeline(steps)


def random_search(
    X: pd.DataFrame,
    y: pd.Series,
    algorithm: str = "lgbm",
    n_iter: int = 30,
    n_folds: int = 3,
    balancing: str = "none",
    progress_callback=None,
) -> dict:
    """Randomized hyperparameter search. Returns best params dict."""
    from sklearn.model_selection import RandomizedSearchCV
    pipe = build_pipeline(X, algorithm, {}, balancing=balancing)
    grid = _RANDOM_GRIDS.get(algorithm, {})
    skf  = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    search = RandomizedSearchCV(
        pipe, grid, n_iter=n_iter,
        cv=skf, scoring="roc_auc",
        random_state=42, n_jobs=-1, refit=True,
    )
    search.fit(X, y)
    if progress_callback:
        progress_callback(n_iter, n_iter, search.best_score_)
    best = {k.replace("model__", ""): v for k, v in search.best_params_.items()}
    return best


def grid_search(
    X: pd.DataFrame,
    y: pd.Series,
    algorithm: str = "lgbm",
    n_folds: int = 3,
    balancing: str = "none",
    progress_callback=None,
) -> dict:
    """Exhaustive grid search. Returns best params dict."""
    from sklearn.model_selection import GridSearchCV
    pipe = build_pipeline(X, algorithm, {}, balancing=balancing)
    grid = _GRID_GRIDS.get(algorithm, {})
    skf  = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    search = GridSearchCV(
        pipe, grid,
        cv=skf, scoring="roc_auc",
        n_jobs=-1, refit=True,
    )
    search.fit(X, y)
    if progress_callback:
        progress_callback(1, 1, search.best_score_)
    best = {k.replace("model__", ""): v for k, v in search.best_params_.items()}
    return best


def _suggest_params(trial, algorithm: str) -> dict:
    """Map an Optuna trial to a params dict for the given algorithm."""
    if algorithm == "lgbm":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 100, 800, step=50),
            "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.2, log=True),
            "max_depth": trial.suggest_int("max_depth", -1, 12),
            "num_leaves": trial.suggest_int("num_leaves", 20, 150),
        }
    if algorithm == "xgb":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 100, 800, step=50),
            "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.2, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 12),
        }
    if algorithm == "rf":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
            "max_depth": trial.suggest_int("max_depth", 3, 20),
        }
    if algorithm == "logreg":
        return {"C": trial.suggest_float("C", 0.001, 100.0, log=True)}
    return {}


def optimize_hyperparams(
    X: pd.DataFrame,
    y: pd.Series,
    algorithm: str = "lgbm",
    n_trials: int = 50,
    n_folds: int = 3,
    use_smote: bool = False,
    balancing: str = "none",
    progress_callback=None,
) -> dict:
    """Run Optuna hyperparameter search. Returns best params dict."""
    try:
        import optuna
        optuna.logging.set_verbosity(optuna.logging.WARNING)
    except ImportError:
        raise ImportError("Instale optuna: pip install optuna")

    _balancing = balancing if balancing != "none" else ("smote_over" if use_smote else "none")
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    completed = [0]

    def objective(trial):
        params = _suggest_params(trial, algorithm)
        scores = []
        for tr_idx, vl_idx in skf.split(X, y):
            X_tr, X_vl = X.iloc[tr_idx], X.iloc[vl_idx]
            y_tr, y_vl = y.iloc[tr_idx], y.iloc[vl_idx]
            pipe = build_pipeline(X_tr, algorithm, params, balancing=_balancing)
            pipe.fit(X_tr, y_tr)
            probs = pipe.predict_proba(X_vl)[:, 1]
            scores.append(roc_auc_score(y_vl, probs))
        completed[0] += 1
        if progress_callback:
            progress_callback(completed[0], n_trials, float(np.mean(scores)))
        return float(np.mean(scores))

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    return study.best_params


def train_cv(
    X: pd.DataFrame,
    y: pd.Series,
    algorithm: str = "lgbm",
    params: dict | None = None,
    n_folds: int = 5,
    use_smote: bool = False,
    balancing: str = "none",
) -> dict:
    """Train with StratifiedKFold CV and return per-fold + aggregate metrics."""
    params = params or {}
    _balancing = balancing if balancing != "none" else ("smote_over" if use_smote else "none")
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

    oof_probs = np.zeros(len(y))
    fold_metrics = []
    importances_list = []

    for fold, (tr_idx, vl_idx) in enumerate(skf.split(X, y)):
        X_tr, X_vl = X.iloc[tr_idx], X.iloc[vl_idx]
        y_tr, y_vl = y.iloc[tr_idx], y.iloc[vl_idx]

        pipe = build_pipeline(X_tr, algorithm, params, balancing=_balancing)
        pipe.fit(X_tr, y_tr)

        probs = pipe.predict_proba(X_vl)[:, 1]
        preds = (probs >= 0.5).astype(int)
        oof_probs[vl_idx] = probs

        metrics = _compute_metrics(y_vl, probs, preds)
        metrics["fold"] = fold + 1
        fold_metrics.append(metrics)

        imp = _get_importances(pipe, X.columns.tolist())
        if imp is not None:
            importances_list.append(imp)

    mean_metrics = {
        k: float(np.mean([f[k] for f in fold_metrics]))
        for k in fold_metrics[0] if k != "fold"
    }

    feature_importances = {}
    if importances_list:
        all_imp = pd.DataFrame(importances_list)
        feature_importances = all_imp.mean().to_dict()

    final_pipe = build_pipeline(X, algorithm, params, balancing=_balancing)
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


def calibrate_model(
    model,
    X: pd.DataFrame,
    y: pd.Series,
    method: str = "sigmoid",
    cal_fraction: float = 0.25,
) -> dict:
    """Post-hoc Platt/isotonic calibration using a held-out calibration set."""
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.model_selection import train_test_split

    _, X_cal, _, y_cal = train_test_split(
        X, y, test_size=cal_fraction, stratify=y, random_state=7
    )

    raw_probs = model.predict_proba(X_cal)[:, 1]

    try:
        from sklearn.frozen import FrozenEstimator
        cal_clf = CalibratedClassifierCV(estimator=FrozenEstimator(model), method=method)
    except ImportError:
        cal_clf = CalibratedClassifierCV(estimator=model, cv="prefit", method=method)
    cal_clf.fit(X_cal, y_cal)
    cal_probs = cal_clf.predict_proba(X_cal)[:, 1]

    brier_before = brier_score_loss(y_cal, raw_probs)
    brier_after  = brier_score_loss(y_cal, cal_probs)

    return {
        "cal_model": cal_clf,
        "method": method,
        "raw_probs": raw_probs,
        "cal_probs": cal_probs,
        "y_eval": y_cal.values,
        "brier_before": float(brier_before),
        "brier_after":  float(brier_after),
        "brier_delta":  float(brier_before - brier_after),
    }


def _compute_metrics(y_true, probs, preds) -> dict:
    return {
        "roc_auc":   roc_auc_score(y_true, probs),
        "pr_auc":    average_precision_score(y_true, probs),
        "f1":        f1_score(y_true, preds, zero_division=0),
        "precision": precision_score(y_true, preds, zero_division=0),
        "recall":    recall_score(y_true, preds, zero_division=0),
        "brier":     brier_score_loss(y_true, probs),
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
