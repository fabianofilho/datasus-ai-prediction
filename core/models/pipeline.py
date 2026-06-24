"""ML training pipeline with cross-validation and optional HPO.

Supported algorithms: LightGBM, XGBoost, CatBoost, Logistic Regression,
Random Forest, Rede Neural (MLP), TabPFN (opcional).
HPO modes: Manual, Random Search, Grid Search, Optuna.
Balancing: None, Class Weight, SMOTE (oversample), SMOTE + Undersampling.
Treatment: per-column encoding (OHE, Ordinal, Target) and scaling (Standard, MinMax).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, average_precision_score, f1_score,
    precision_score, recall_score, brier_score_loss,
)


# Base algorithms always available
ALGORITHMS: dict[str, str] = {
    "LightGBM": "lgbm",
    "XGBoost": "xgb",
    "CatBoost": "catboost",
    "Logistic Regression": "logreg",
    "Random Forest": "rf",
    "Rede Neural (MLP)": "mlp",
}

# Algorithm families — used by the training screen to pick the right
# learning-curve perspective (epochs for the net, boosting rounds for trees).
BOOSTING_ALGORITHMS: set[str] = {"lgbm", "xgb", "catboost"}
NEURAL_ALGORITHMS: set[str] = {"mlp"}

# TabPFN: always listed, but only usable if torch+tabpfn installed
TABPFN_AVAILABLE: bool = False
try:
    import tabpfn as _tabpfn  # noqa: F401
    ALGORITHMS["TabPFN"] = "tabpfn"
    TABPFN_AVAILABLE = True
except ImportError:
    ALGORITHMS["TabPFN"] = "tabpfn"  # keep in list, build_pipeline will raise gracefully

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
    "catboost": {
        "model__iterations":   [100, 200, 300, 500],
        "model__learning_rate": [0.01, 0.05, 0.1, 0.2],
        "model__depth":        [4, 6, 8, 10],
    },
    "mlp": {
        "model__hidden_layer_sizes": [(64,), (128,), (64, 32), (128, 64), (100, 50, 25)],
        "model__alpha":              [1e-4, 1e-3, 1e-2],
        "model__learning_rate_init": [1e-3, 5e-3, 1e-2],
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
    "catboost": {
        "model__iterations":    [100, 300, 500],
        "model__learning_rate": [0.05, 0.1],
        "model__depth":         [4, 6, 8],
    },
    "mlp": {
        "model__hidden_layer_sizes": [(64,), (64, 32)],
        "model__alpha":              [1e-4, 1e-3],
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
            n_estimators=params.get("n_estimators", 150),
            learning_rate=params.get("learning_rate", 0.05),
            max_depth=params.get("max_depth", 6),
            subsample=params.get("subsample", 0.8),
            colsample_bytree=params.get("colsample_bytree", 0.8),
            eval_metric="logloss",
            tree_method="hist",
            verbosity=0,
            n_jobs=-1,
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
    if algorithm == "catboost":
        from catboost import CatBoostClassifier
        return CatBoostClassifier(
            iterations=params.get("iterations", 300),
            learning_rate=params.get("learning_rate", 0.05),
            depth=params.get("depth", 6),
            auto_class_weights="Balanced" if class_weight else None,
            random_seed=42,
            verbose=0,
            allow_writing_files=False,
        )
    if algorithm == "mlp":
        from sklearn.neural_network import MLPClassifier
        # class_weight não é suportado por MLPClassifier — balanceamento via SMOTE.
        return MLPClassifier(
            hidden_layer_sizes=params.get("hidden_layer_sizes", (64, 32)),
            alpha=params.get("alpha", 1e-4),
            learning_rate_init=params.get("learning_rate_init", 1e-3),
            max_iter=params.get("max_iter", 300),
            early_stopping=params.get("early_stopping", True),
            n_iter_no_change=10,
            random_state=42,
        )
    if algorithm == "tabpfn":
        try:
            from tabpfn import TabPFNClassifier
            return TabPFNClassifier(n_estimators=8, device="auto", random_state=42)
        except ImportError:
            raise ImportError(
                "TabPFN não está instalado. Execute: pip install tabpfn"
            )
    raise ValueError(f"Unknown algorithm: {algorithm}")


def _class_weight_for_balancing(balancing: str) -> str | None:
    """Return sklearn class_weight value given our balancing setting."""
    return "balanced" if balancing == "class_weight" else None


def _safe_over_sampler(random_state: int = 42):
    """SMOTE que ajusta k_neighbors ao tamanho da classe minoritária no fit.

    O default k_neighbors=5 exige >=6 amostras minoritárias; em CV com desfecho
    raro o fold de treino pode ter menos e o SMOTE quebra. Aqui o k é reduzido
    dinamicamente (e o resampling é pulado se houver <=1 amostra minoritária).
    """
    from imblearn.over_sampling import SMOTE

    class _SafeSMOTE(SMOTE):
        def fit_resample(self, X, y):  # noqa: N803
            _, counts = np.unique(np.asarray(y), return_counts=True)
            n_min = int(counts.min()) if len(counts) else 0
            if n_min <= 1:
                return X, y  # nada a sintetizar com segurança
            self.k_neighbors = max(1, min(5, n_min - 1))
            return super().fit_resample(X, y)

    return _SafeSMOTE(random_state=random_state)


def _safe_combine_sampler(random_state: int = 42):
    """SMOTETomek com o SMOTE interno auto-ajustável; cai para SMOTE se indisponível."""
    try:
        from imblearn.combine import SMOTETomek
        return SMOTETomek(random_state=random_state, smote=_safe_over_sampler(random_state))
    except ImportError:
        return _safe_over_sampler(random_state)


class SentinelReplacer(BaseEstimator, TransformerMixin):
    """Replace DATASUS sentinel values (e.g. 9, 99 = 'Ignorado') with NaN.

    Applied as the first pipeline step so downstream imputers fill them
    with the median / mode of the real data distribution.
    """

    def __init__(self, sentinels: list | None = None):
        self.sentinels = sentinels or []

    def fit(self, X, y=None):  # noqa: N803
        return self

    def transform(self, X):  # noqa: N803
        if not self.sentinels:
            return X
        if isinstance(X, pd.DataFrame):
            X = X.copy()
            for v in self.sentinels:
                X = X.replace(v, np.nan)
        else:
            X = X.astype(float)
            for v in self.sentinels:
                X[X == v] = np.nan
        return X


def _build_preprocessor(
    X: pd.DataFrame,
    treatment: dict | None,
    algorithm: str,
) -> ColumnTransformer:
    """Build ColumnTransformer from treatment config."""
    from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, MinMaxScaler

    if treatment is None:
        num_cols = X.select_dtypes(include="number").columns.tolist()
        cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
        num_default, cat_default, overrides = "none", "ohe", {}
    else:
        # Use explicit cols from config (respects type overrides made by user)
        num_cols = treatment.get("num_cols") or X.select_dtypes(include="number").columns.tolist()
        cat_cols = treatment.get("cat_cols") or X.select_dtypes(include=["object", "category"]).columns.tolist()
        num_default = treatment.get("num_default", "none")
        cat_default = treatment.get("cat_default", "ohe")
        overrides   = treatment.get("overrides", {})
    # Restrict to columns actually present in X
    num_cols = [c for c in num_cols if c in X.columns]
    cat_cols = [c for c in cat_cols if c in X.columns]

    # Effective treatment per column
    num_eff = {c: overrides.get(c, num_default) for c in num_cols}
    cat_eff = {c: overrides.get(c, cat_default) for c in cat_cols}

    # Group by treatment type
    num_groups: dict[str, list] = {}
    for c, t in num_eff.items():
        num_groups.setdefault(t, []).append(c)

    cat_groups: dict[str, list] = {}
    for c, t in cat_eff.items():
        cat_groups.setdefault(t, []).append(c)

    transformers = []

    # ── Numerical ─────────────────────────────────────────────────────────────
    for t, cols in num_groups.items():
        if t == "drop" or not cols:
            continue
        inner: list = [("impute", SimpleImputer(strategy="median"))]
        if t == "standard":
            inner.append(("scale", StandardScaler()))
        elif t == "minmax":
            inner.append(("scale", MinMaxScaler()))
        elif t == "robust":
            from sklearn.preprocessing import RobustScaler
            inner.append(("scale", RobustScaler()))
        elif t == "bin":
            from sklearn.preprocessing import KBinsDiscretizer
            inner.append(("bin", KBinsDiscretizer(n_bins=5, encode="ordinal", strategy="quantile")))
        transformers.append((f"num_{t}", Pipeline(inner), cols))

    # ── Categorical ───────────────────────────────────────────────────────────
    for t, cols in cat_groups.items():
        if t == "drop" or not cols:
            continue
        if t == "target":
            try:
                from sklearn.preprocessing import TargetEncoder
                transformers.append((f"cat_{t}", TargetEncoder(smooth="auto"), cols))
            except ImportError:
                # Fallback: ordinal
                enc = Pipeline([
                    ("impute", SimpleImputer(strategy="most_frequent")),
                    ("encode", OrdinalEncoder(
                        handle_unknown="use_encoded_value", unknown_value=-1)),
                ])
                transformers.append((f"cat_{t}", enc, cols))
        elif t in ("ordinal", "none"):   # "none" = ordinal simples (recomendado para árvores)
            enc = Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("encode", OrdinalEncoder(
                    handle_unknown="use_encoded_value", unknown_value=-1)),
            ])
            transformers.append((f"cat_{t}", enc, cols))
        else:  # ohe (default)
            enc = Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ])
            transformers.append((f"cat_{t}", enc, cols))

    if not transformers:
        # Fallback: impute all available columns
        fallback_cols = num_cols or X.columns.tolist()
        transformers = [("num_none", SimpleImputer(strategy="median"), fallback_cols)]

    return ColumnTransformer(transformers, remainder="drop")


TABPFN_MAX_TRAIN_SAMPLES = 10_000   # hard limit — TabPFN não é escalável além disso
TABPFN_WARN_TRAIN_SAMPLES = 1_000   # acima disso o desempenho pode degradar


def build_pipeline(
    X: pd.DataFrame,
    algorithm: str = "lgbm",
    params: dict | None = None,
    use_smote: bool = False,
    balancing: str = "none",
    treatment: dict | None = None,
) -> Pipeline:
    """Build full sklearn/imblearn Pipeline with preprocessing + optional balancing."""
    params = params or {}

    if algorithm == "tabpfn" and len(X) > TABPFN_MAX_TRAIN_SAMPLES:
        raise ValueError(
            f"TabPFN suporta no máximo {TABPFN_MAX_TRAIN_SAMPLES:,} amostras de treino, "
            f"mas foram fornecidas {len(X):,}. "
            "Reduza o tamanho da amostra no Passo 2 ou escolha outro algoritmo."
        )

    sentinels = list((treatment or {}).get("null_sentinels", []))
    preprocessor = _build_preprocessor(X, treatment, algorithm)
    cw = _class_weight_for_balancing(balancing)
    steps: list = []
    if sentinels:
        steps.append(("sentinel", SentinelReplacer(sentinels)))
    steps.append(("prep", preprocessor))

    # Add StandardScaler for logreg / MLP when numerics aren't already scaled
    _num_scaled = treatment is not None and treatment.get("num_default") in ("standard", "minmax")
    if algorithm in ("logreg", "mlp") and not _num_scaled:
        steps.append(("scaler", StandardScaler()))

    # Resolve effective resampling
    do_smote_over  = balancing == "smote_over" or use_smote
    do_smote_under = balancing == "smote_under"

    if do_smote_under or do_smote_over:
        try:
            from imblearn.pipeline import Pipeline as ImbPipeline
            if do_smote_under:
                steps.append(("resample", _safe_combine_sampler()))
            else:
                steps.append(("resample", _safe_over_sampler()))
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
    treatment: dict | None = None,
    progress_callback=None,
) -> dict:
    """Randomized hyperparameter search. Returns best params dict."""
    from sklearn.model_selection import RandomizedSearchCV
    pipe = build_pipeline(X, algorithm, {}, balancing=balancing, treatment=treatment)
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
    treatment: dict | None = None,
    progress_callback=None,
) -> dict:
    """Exhaustive grid search. Returns best params dict."""
    from sklearn.model_selection import GridSearchCV
    pipe = build_pipeline(X, algorithm, {}, balancing=balancing, treatment=treatment)
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
            "n_estimators": trial.suggest_int("n_estimators", 50, 200, step=50),
            "learning_rate": trial.suggest_float("learning_rate", 0.05, 0.3, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 6),
        }
    if algorithm == "rf":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
            "max_depth": trial.suggest_int("max_depth", 3, 20),
        }
    if algorithm == "logreg":
        return {"C": trial.suggest_float("C", 0.001, 100.0, log=True)}
    if algorithm == "catboost":
        return {
            "iterations":    trial.suggest_int("iterations", 100, 800, step=50),
            "learning_rate": trial.suggest_float("learning_rate", 0.005, 0.2, log=True),
            "depth":         trial.suggest_int("depth", 4, 10),
        }
    if algorithm == "mlp":
        _hl = trial.suggest_categorical(
            "hidden_layer_sizes", ["64", "128", "64,32", "128,64", "100,50,25"]
        )
        return {
            "hidden_layer_sizes": tuple(int(x) for x in _hl.split(",")),
            "alpha":              trial.suggest_float("alpha", 1e-5, 1e-2, log=True),
            "learning_rate_init": trial.suggest_float("learning_rate_init", 1e-4, 1e-2, log=True),
        }
    return {}


def optimize_hyperparams(
    X: pd.DataFrame,
    y: pd.Series,
    algorithm: str = "lgbm",
    n_trials: int = 50,
    n_folds: int = 3,
    use_smote: bool = False,
    balancing: str = "none",
    treatment: dict | None = None,
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
            pipe = build_pipeline(X_tr, algorithm, params,
                                  balancing=_balancing, treatment=treatment)
            pipe.fit(X_tr, y_tr)
            probs = pipe.predict_proba(X_vl)[:, 1]
            scores.append(roc_auc_score(y_vl, probs))
        completed[0] += 1
        if progress_callback:
            progress_callback(completed[0], n_trials, float(np.mean(scores)))
        return float(np.mean(scores))

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    best = dict(study.best_params)
    # MLP: hidden_layer_sizes é sugerido como string categórica ("64,32") —
    # study.best_params guarda a string, então converte de volta para tupla.
    _hl = best.get("hidden_layer_sizes")
    if isinstance(_hl, str):
        best["hidden_layer_sizes"] = tuple(int(x) for x in _hl.split(","))
    return best


def train_cv(
    X: pd.DataFrame,
    y: pd.Series,
    algorithm: str = "lgbm",
    params: dict | None = None,
    n_folds: int = 5,
    use_smote: bool = False,
    balancing: str = "none",
    treatment: dict | None = None,
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

        pipe = build_pipeline(X_tr, algorithm, params,
                              balancing=_balancing, treatment=treatment)
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
        k: float(np.nanmean([f[k] for f in fold_metrics if k in f]))
        for k in fold_metrics[0] if k != "fold"
    }
    # Garantir que nenhuma métrica seja nan — substituir por 0.0
    mean_metrics = {k: (v if not (v != v) else 0.0) for k, v in mean_metrics.items()}

    feature_importances = {}
    if importances_list:
        all_imp = pd.DataFrame(importances_list).fillna(0)
        feature_importances = all_imp.mean().to_dict()

    final_pipe = build_pipeline(X, algorithm, params,
                                balancing=_balancing, treatment=treatment)
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
    """Calibração pós-hoc (Platt/isotônica) com avaliação honesta em held-out.

    Para o Brier antes/depois não ser medido in-sample (o que dava ~0 porque o
    modelo já tinha visto os dados), particionamos em 50% fit / 25% calibração /
    25% avaliação: o modelo base é re-treinado só no fit (não vê cal nem eval), o
    calibrador é ajustado no cal, e os Briers são medidos no eval, que nenhum dos
    dois viu. Se a partição estratificada falhar (desfecho muito raro), cai para o
    modo prefit sobre uma fração de calibração.
    """
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.model_selection import train_test_split
    from sklearn.base import clone

    def _frozen_cal(est):
        try:
            from sklearn.frozen import FrozenEstimator
            return CalibratedClassifierCV(estimator=FrozenEstimator(est), method=method)
        except ImportError:
            return CalibratedClassifierCV(estimator=est, cv="prefit", method=method)

    try:
        # 50% fit (re-treina o base) · 25% calibração · 25% avaliação (held-out de ambos)
        X_fit, X_tmp, y_fit, y_tmp = train_test_split(
            X, y, test_size=0.5, stratify=y, random_state=7)
        X_cal, X_eval, y_cal, y_eval = train_test_split(
            X_tmp, y_tmp, test_size=0.5, stratify=y_tmp, random_state=7)
        base = clone(model)
        base.fit(X_fit, y_fit)
        raw_probs = base.predict_proba(X_eval)[:, 1]
        cal_clf = _frozen_cal(base)
        cal_clf.fit(X_cal, y_cal)
        cal_probs = cal_clf.predict_proba(X_eval)[:, 1]
        y_out = y_eval
    except Exception:
        # Fallback robusto: calibra o modelo dado numa fração (sem re-treino).
        # Avalia in-sample (menos honesto, mas não quebra com desfecho raríssimo).
        _, X_cal, _, y_cal = train_test_split(
            X, y, test_size=cal_fraction, stratify=y, random_state=7)
        raw_probs = model.predict_proba(X_cal)[:, 1]
        cal_clf = _frozen_cal(model)
        cal_clf.fit(X_cal, y_cal)
        cal_probs = cal_clf.predict_proba(X_cal)[:, 1]
        y_out = y_cal

    brier_before = brier_score_loss(y_out, raw_probs)
    brier_after  = brier_score_loss(y_out, cal_probs)

    return {
        "cal_model": cal_clf,
        "method": method,
        "raw_probs": raw_probs,
        "cal_probs": cal_probs,
        "y_eval": np.asarray(y_out),
        "brier_before": float(brier_before),
        "brier_after":  float(brier_after),
        "brier_delta":  float(brier_before - brier_after),
    }


def _compute_metrics(y_true, probs, preds) -> dict:
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y_true, preds)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    else:
        specificity = float("nan")
    return {
        "roc_auc":     roc_auc_score(y_true, probs),
        "pr_auc":      average_precision_score(y_true, probs),
        "f1":          f1_score(y_true, preds, zero_division=0),
        "precision":   precision_score(y_true, preds, zero_division=0),
        "recall":      recall_score(y_true, preds, zero_division=0),
        "specificity": specificity,
        "brier":       brier_score_loss(y_true, probs),
    }


def _get_importances(pipe: Pipeline, feature_names: list[str]) -> dict | None:
    """Extract feature importances using pipeline's actual output feature names."""
    model = pipe[-1]
    # Try to get feature names after transformation (handles OHE expansion)
    try:
        actual_names = list(pipe.named_steps["prep"].get_feature_names_out())
    except Exception:
        actual_names = feature_names

    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_
        if len(imp) == len(actual_names):
            return dict(zip(actual_names, imp))
    elif hasattr(model, "coef_"):
        imp = np.abs(model.coef_[0])
        if len(imp) == len(actual_names):
            return dict(zip(actual_names, imp))
    return None


# ══════════════════════════════════════════════════════════════════════════════
# Curva de aprendizado ao vivo — uma perspectiva por família de algoritmo
# ══════════════════════════════════════════════════════════════════════════════
#   • Rede neural (MLP)  → ROC-AUC por época   (treino incremental real)
#   • Boosting (lgbm/xgb/catboost) → ROC-AUC por árvore adicionada
#   • Demais (logreg/rf/tabpfn)    → ROC-AUC por volume de dados
#
# Estas curvas são apenas para visualização do aprendizado. As métricas oficiais
# continuam vindo de train_cv / holdout / validação temporal, intocados.

def _safe_auc(y, p) -> float:
    """ROC-AUC tolerante a classe única ou falha — devolve 0.5 nesses casos."""
    try:
        y_arr = np.asarray(y)
        if len(np.unique(y_arr)) < 2:
            return 0.5
        return float(roc_auc_score(y_arr, p))
    except Exception:
        return 0.5


def _even_indices(n: int, k: int) -> list[int]:
    """Até k índices espaçados uniformemente em [0, n-1] (sempre inclui o último)."""
    if n <= 0:
        return []
    if n <= k:
        return list(range(n))
    return sorted({int(round(x)) for x in np.linspace(0, n - 1, k)})


def _preprocess_fit_transform(X_tr, X_val, algorithm: str, treatment: dict | None):
    """Ajusta só o pré-processamento no treino e devolve arrays densos (tr, val).

    Espelha o build_pipeline (sentinel + prep [+ scaler p/ logreg/mlp]) mas para
    antes do modelo, para que um booster/MLP possa ser treinado com eval_set.
    """
    sentinels = list((treatment or {}).get("null_sentinels", []))
    steps: list = []
    if sentinels:
        steps.append(("sentinel", SentinelReplacer(sentinels)))
    steps.append(("prep", _build_preprocessor(X_tr, treatment, algorithm)))
    _num_scaled = treatment is not None and treatment.get("num_default") in ("standard", "minmax")
    if algorithm in ("logreg", "mlp") and not _num_scaled:
        steps.append(("scaler", StandardScaler()))
    pre = Pipeline(steps)
    Xt_tr = pre.fit_transform(X_tr)
    Xt_val = pre.transform(X_val)
    Xt_tr = np.asarray(Xt_tr)
    Xt_val = np.asarray(Xt_val)
    try:
        names = list(pre.named_steps["prep"].get_feature_names_out())
        if len(names) != Xt_tr.shape[1]:
            raise ValueError
    except Exception:
        names = [f"f{i}" for i in range(Xt_tr.shape[1])]
    return Xt_tr, Xt_val, names


def _boosting_round_aucs(algorithm, Xt, y_tr, Xv, y_val, params: dict):
    """ROC-AUC por round (treino, validação) + modelo treinado para lgbm/xgb/catboost.

    Devolve (train_aucs, val_aucs, model) — o modelo permite extrair a estrutura
    de cada árvore para a visualização do boosting.
    """
    if algorithm == "lgbm":
        import lightgbm as lgb
        from lightgbm import LGBMClassifier
        ev: dict = {}
        m = LGBMClassifier(
            n_estimators=int(params.get("n_estimators", 200)),
            learning_rate=params.get("learning_rate", 0.05),
            max_depth=params.get("max_depth", -1),
            num_leaves=params.get("num_leaves", 31),
            random_state=42, verbose=-1,
        )
        m.fit(
            Xt, y_tr, eval_set=[(Xt, y_tr), (Xv, y_val)],
            eval_names=["train", "val"], eval_metric="auc",
            callbacks=[lgb.record_evaluation(ev)],
        )
        return list(ev["train"]["auc"]), list(ev["val"]["auc"]), m

    if algorithm == "xgb":
        from xgboost import XGBClassifier
        m = XGBClassifier(
            n_estimators=int(params.get("n_estimators", 200)),
            learning_rate=params.get("learning_rate", 0.05),
            max_depth=params.get("max_depth", 6),
            eval_metric="auc", tree_method="hist", verbosity=0,
            n_jobs=-1, random_state=42,
        )
        m.fit(Xt, y_tr, eval_set=[(Xt, y_tr), (Xv, y_val)], verbose=False)
        er = m.evals_result()
        keys = list(er.keys())  # validation_0 = treino, validation_1 = validação
        tr = list(er[keys[0]]["auc"])
        vl = list(er[keys[1]]["auc"]) if len(keys) > 1 else tr
        return tr, vl, m

    if algorithm == "catboost":
        from catboost import CatBoostClassifier
        m = CatBoostClassifier(
            iterations=int(params.get("iterations", params.get("n_estimators", 200))),
            learning_rate=params.get("learning_rate", 0.05),
            depth=params.get("depth", 6),
            eval_metric="AUC", random_seed=42, verbose=0,
            allow_writing_files=False,
            # mantém nº de árvores == nº de rounds avaliados (senão use_best_model
            # trunca o modelo e os últimos rounds da curva ficam sem árvore)
            use_best_model=False,
        )
        m.fit(Xt, y_tr, eval_set=[(Xt, y_tr), (Xv, y_val)])
        er = m.get_evals_result()  # learn, validation_0 (treino), validation_1 (val)
        vl = er.get("validation_1", {}).get("AUC") or er.get("validation_0", {}).get("AUC") or []
        tr = er.get("validation_0", {}).get("AUC") or list(vl)
        return list(tr), list(vl), m

    return [], [], None


def _staged_proba(algorithm, model, X, k):
    """Probabilidade prevista usando apenas as primeiras k árvores (predição acumulada).

    Permite ver o resíduo (y - p) encolhendo conforme as árvores são somadas.
    """
    k = max(1, int(k))
    if algorithm == "lgbm":
        return model.predict_proba(X, num_iteration=k)[:, 1]
    if algorithm == "xgb":
        return model.predict_proba(X, iteration_range=(0, k))[:, 1]
    if algorithm == "catboost":
        return model.predict_proba(X, ntree_end=k)[:, 1]
    return model.predict_proba(X)[:, 1]


# ── Estado estrutural para visualizar o aprendizado ───────────────────────────
# Caps de exibição (apenas para o desenho — o modelo real usa tudo).
_NET_MAX_IN = 10      # neurônios de entrada exibidos
_NET_MAX_HID = 14     # neurônios por camada oculta exibidos
_TREE_MAX_DEPTH = 4   # profundidade máxima desenhada da árvore


def _clean_feat(name: str) -> str:
    """Remove o prefixo do ColumnTransformer ('num_none__feat0' -> 'feat0')."""
    s = str(name)
    return s.rsplit("__", 1)[-1] if "__" in s else s


def _net_state(prev_coefs, coefs, feat_names, epoch: int) -> dict:
    """Snapshot da rede para desenho: pesos por camada (recortados), magnitude
    do passo de backprop (|Δpesos|) por camada e por aresta exibida."""
    n_in = coefs[0].shape[0]
    real_sizes = [n_in] + [c.shape[1] for c in coefs]
    caps = []
    for li, s in enumerate(real_sizes):
        if li == 0:
            caps.append(min(s, _NET_MAX_IN))
        elif li == len(real_sizes) - 1:
            caps.append(s)  # saída (1)
        else:
            caps.append(min(s, _NET_MAX_HID))

    weights, dW, updates = [], [], []
    wmax, dmax = 1e-9, 1e-9
    for li, C in enumerate(coefs):
        w = C[:caps[li], :caps[li + 1]]
        weights.append(w.tolist())
        wmax = max(wmax, float(np.abs(w).max()) if w.size else 0.0)
        if prev_coefs is not None and prev_coefs[li].shape == C.shape:
            full_d = C - prev_coefs[li]
        else:
            full_d = C
        updates.append(float(np.linalg.norm(full_d)))
        d = np.abs(full_d[:caps[li], :caps[li + 1]])
        dW.append(d.tolist())
        dmax = max(dmax, float(d.max()) if d.size else 0.0)

    in_names = [_clean_feat(feat_names[i]) if i < len(feat_names) else f"x{i}"
                for i in range(caps[0])]
    return {
        "kind": "net", "epoch": epoch,
        "real_sizes": real_sizes, "disp_sizes": caps,
        "weights": weights, "dW": dW, "updates": updates,
        "wmax": wmax, "dmax": dmax, "in_names": in_names,
    }


def _net_caps(real_sizes):
    """Tamanhos exibidos por camada (mesma regra do _net_state)."""
    caps = []
    for li, s in enumerate(real_sizes):
        if li == 0:
            caps.append(min(s, _NET_MAX_IN))
        elif li == len(real_sizes) - 1:
            caps.append(s)
        else:
            caps.append(min(s, _NET_MAX_HID))
    return caps


def _mlp_forward_frames(clf, X_val, y_val, feat_names, raw_X=None, n_samples=4):
    """Frames do forward pass: alguns exemplos reais atravessando a rede já treinada.

    Para cada exemplo, calcula as ativações camada a camada (entrada → ocultas →
    saída) usando os pesos atuais. Devolve uma lista de dicts (um por exemplo) com
    as ativações recortadas e normalizadas, valores de entrada, predição e rótulo.
    """
    coefs = clf.coefs_
    intercepts = clf.intercepts_
    act = getattr(clf, "activation", "relu")

    def f_hidden(z):
        if act == "tanh":
            return np.tanh(z)
        if act == "logistic":
            return 1.0 / (1.0 + np.exp(-z))
        if act == "identity":
            return z
        return np.maximum(0.0, z)  # relu (padrão)

    def f_out(z):
        return 1.0 / (1.0 + np.exp(-z))  # binário → logística

    n_in = coefs[0].shape[0]
    real_sizes = [n_in] + [c.shape[1] for c in coefs]
    caps = _net_caps(real_sizes)
    in_names = [_clean_feat(feat_names[i]) if i < len(feat_names) else f"x{i}"
                for i in range(caps[0])]
    weights = [np.asarray(c)[:caps[li], :caps[li + 1]].tolist() for li, c in enumerate(coefs)]
    wmax = max(1e-9, max(float(np.abs(np.asarray(c)[:caps[li], :caps[li + 1]]).max())
                         for li, c in enumerate(coefs)))

    # raw_X (DataFrame original, alinhado linha a linha com X_val) permite mostrar
    # o valor real do paciente no neurônio de entrada, em vez do z-score.
    raw_ok = hasattr(raw_X, "columns") and hasattr(raw_X, "iloc")

    X_val = np.asarray(X_val)
    y_val = np.asarray(y_val)
    probs = clf.predict_proba(X_val)[:, 1]
    order = np.argsort(probs)
    n_samples = min(n_samples, len(order))
    if n_samples <= 0:
        return []
    pick = [int(order[int(round(k))]) for k in np.linspace(0, len(order) - 1, n_samples)]

    frames = []
    for si, idx in enumerate(pick):
        x = X_val[idx].astype(float)
        acts = [x]
        a = x
        for i, (W, b) in enumerate(zip(coefs, intercepts)):
            z = a @ W + b
            a = f_out(z) if i == len(coefs) - 1 else f_hidden(z)
            acts.append(np.asarray(a))
        capped = [np.asarray(av).ravel()[:caps[li]].tolist() for li, av in enumerate(acts)]
        in_real = []
        for nm in in_names:
            if raw_ok and nm in raw_X.columns:
                try:
                    in_real.append(raw_X.iloc[idx][nm])
                except Exception:
                    in_real.append(None)
            else:
                in_real.append(None)
        frames.append({
            "sample": si + 1, "n_samples": n_samples,
            "real_sizes": real_sizes, "caps": caps,
            "activations": capped, "weights": weights, "wmax": wmax,
            "in_names": in_names, "in_values": x.ravel()[:caps[0]].tolist(),
            "in_real": in_real,
            "pred": float(np.asarray(acts[-1]).ravel()[0]), "y_true": int(y_val[idx]),
        })
    return frames


def _extract_trees(algorithm, model, indices, feat_names) -> dict:
    """{tree_idx: [nós normalizados]} para os índices pedidos.

    Cada nó: {id, parent, side('L'/'R'/None), depth, label, is_leaf}.
    Estrutura extraída uma única vez do modelo já treinado.
    """
    if model is None or not indices:
        return {}

    def fname(i):
        try:
            return _clean_feat(feat_names[int(i)])
        except Exception:
            return f"f{i}"

    want = set(int(i) for i in indices)
    out: dict = {}

    try:
        if algorithm == "lgbm":
            tree_info = model.booster_.dump_model().get("tree_info", [])
            for ti in want:
                if ti >= len(tree_info):
                    continue
                root = tree_info[ti]["tree_structure"]
                nodes: list = []
                ctr = [0]

                def rec(node, parent, side, depth):
                    nid = ctr[0]; ctr[0] += 1
                    if "split_feature" in node:
                        lbl = f"{fname(node['split_feature'])} ≤ {node.get('threshold', 0):.2f}"
                        nodes.append({"id": nid, "parent": parent, "side": side,
                                      "depth": depth, "label": lbl, "is_leaf": False})
                        rec(node["left_child"], nid, "L", depth + 1)
                        rec(node["right_child"], nid, "R", depth + 1)
                    else:
                        nodes.append({"id": nid, "parent": parent, "side": side,
                                      "depth": depth, "label": f"{node.get('leaf_value', 0):.2f}",
                                      "is_leaf": True})
                rec(root, None, None, 0)
                out[ti] = nodes

        elif algorithm == "xgb":
            df = model.get_booster().trees_to_dataframe()

            def xfeat(ft):
                s = str(ft)
                return fname(int(s[1:])) if (s.startswith("f") and s[1:].isdigit()) else s

            for ti in want:
                sub = df[df["Tree"] == ti]
                if sub.empty:
                    continue
                parent, side = {}, {}
                for row in sub.itertuples():
                    if str(row.Feature) != "Leaf":
                        parent[row.Yes] = row.ID; side[row.Yes] = "L"
                        parent[row.No] = row.ID; side[row.No] = "R"
                idmap = {row.ID: k for k, row in enumerate(sub.itertuples())}

                def depth_of(idv):
                    d, cur = 0, idv
                    while cur in parent:
                        cur = parent[cur]; d += 1
                    return d
                nodes = []
                for row in sub.itertuples():
                    leaf = str(row.Feature) == "Leaf"
                    lbl = f"{row.Gain:.2f}" if leaf else f"{xfeat(row.Feature)} ≤ {row.Split:.2f}"
                    par = parent.get(row.ID)
                    nodes.append({"id": idmap[row.ID],
                                  "parent": idmap.get(par) if par is not None else None,
                                  "side": side.get(row.ID), "depth": depth_of(row.ID),
                                  "label": lbl, "is_leaf": leaf})
                out[ti] = nodes

        elif algorithm == "catboost":
            import tempfile, os, json
            p = os.path.join(tempfile.gettempdir(), "_cb_tree_viz.json")
            model.save_model(p, format="json")
            with open(p) as fh:
                js = json.load(fh)
            ot = js.get("oblivious_trees", [])
            for ti in want:
                if ti >= len(ot):
                    continue
                splits = ot[ti].get("splits", [])
                depth = len(splits)
                nodes = []
                ctr = [0]

                def rec(level, parent, side, d):
                    nid = ctr[0]; ctr[0] += 1
                    if level >= len(splits):
                        nodes.append({"id": nid, "parent": parent, "side": side,
                                      "depth": d, "label": "folha", "is_leaf": True})
                        return
                    s = splits[level]
                    fi = s.get("float_feature_index", s.get("feature_index", 0))
                    lbl = f"{fname(fi)} ≤ {s.get('border', 0.0):.2f}"
                    nodes.append({"id": nid, "parent": parent, "side": side,
                                  "depth": d, "label": lbl, "is_leaf": False})
                    rec(level + 1, nid, "L", d + 1)
                    rec(level + 1, nid, "R", d + 1)
                rec(0, None, None, 0)
                out[ti] = nodes
    except Exception:
        return out
    return out


def training_curve(
    X_tr, y_tr, X_val, y_val,
    algorithm: str = "lgbm",
    params: dict | None = None,
    treatment: dict | None = None,
    progress_callback=None,
    max_points: int = 40,
    extra_callback=None,
    forward_samples: int = 4,
) -> dict:
    """Trajetória de aprendizado passo a passo para visualização ao vivo.

    Devolve {"mode", "x_label", "steps", "train", "val", "metric"} onde mode é
    "epoch" (rede neural), "boosting" (árvores) ou "volume" (demais modelos).
    Chama progress_callback(done, total, x_value, step_label, train_auc, val_auc, state)
    a cada passo. `state` traz a estrutura para desenhar o aprendizado:
      • rede neural → {"kind":"net", pesos/Δpesos por camada, ...}
      • boosting    → {"kind":"resid", resíduo (y-p) por paciente encolhendo, ...}
      • volume      → None

    extra_callback(done, total, state) recebe a animação secundária ao final:
      • rede neural → {"kind":"forward", ...} (exemplos atravessando a rede)
      • boosting    → {"kind":"tree", ...} (algumas árvores reais do comitê)
    """
    params = params or {}
    y_tr = np.asarray(y_tr)
    y_val = np.asarray(y_val)

    # ── Rede neural: trajetória real por época via partial_fit ────────────────
    if algorithm in NEURAL_ALGORITHMS:
        from sklearn.neural_network import MLPClassifier
        Xt, Xv, feat_names = _preprocess_fit_transform(X_tr, X_val, "mlp", treatment)
        n_epochs = max(5, min(int(params.get("max_iter", 25)), 60))
        clf = MLPClassifier(
            hidden_layer_sizes=params.get("hidden_layer_sizes", (64, 32)),
            alpha=params.get("alpha", 1e-4),
            learning_rate_init=params.get("learning_rate_init", 1e-3),
            random_state=42,
        )
        steps, tr, vl = [], [], []
        classes = np.array([0, 1])
        prev_coefs = None
        for ep in range(1, n_epochs + 1):
            clf.partial_fit(Xt, y_tr, classes=classes)
            ta = _safe_auc(y_tr, clf.predict_proba(Xt)[:, 1])
            va = _safe_auc(y_val, clf.predict_proba(Xv)[:, 1])
            steps.append(ep); tr.append(ta); vl.append(va)
            state = _net_state(prev_coefs, clf.coefs_, feat_names, ep)
            prev_coefs = [c.copy() for c in clf.coefs_]
            if progress_callback:
                progress_callback(ep, n_epochs, ep, f"Época {ep}/{n_epochs}", ta, va, state)

        # ── Forward pass: exemplos reais atravessando a rede já treinada ──────
        if extra_callback is not None:
            try:
                frames = _mlp_forward_frames(clf, Xv, y_val, feat_names,
                                             raw_X=X_val, n_samples=forward_samples)
                total_steps = sum(len(fr["activations"]) for fr in frames) or 1
                done = 0
                for fr in frames:
                    for li in range(len(fr["activations"])):
                        done += 1
                        fwd = dict(fr)
                        fwd["kind"] = "forward"
                        fwd["active_layer"] = li
                        extra_callback(done, total_steps, fwd)
            except Exception:
                pass

        return {"mode": "epoch", "x_label": "Época",
                "steps": steps, "train": tr, "val": vl, "metric": "roc_auc"}

    # ── Boosting: resíduo (y - p) encolhendo a cada árvore (animação principal) ─
    if algorithm in BOOSTING_ALGORITHMS:
        Xt, Xv, feat_names = _preprocess_fit_transform(X_tr, X_val, algorithm, treatment)
        tr_curve, vl_curve, model = _boosting_round_aucs(algorithm, Xt, y_tr, Xv, y_val, params)
        n = len(vl_curve)
        idx = _even_indices(n, max_points)

        # Amostra balanceada de validação p/ ver o resíduo encolher (estável entre rounds)
        pos_i = np.where(y_val == 1)[0][:50]
        neg_i = np.where(y_val == 0)[0][:50]
        sel = np.concatenate([pos_i, neg_i])
        Xv_sel = Xv[sel]
        y_sel = [int(v) for v in y_val[sel]]

        steps, tr, vl = [], [], []
        for j, i in enumerate(idx, 1):
            steps.append(i + 1)
            tr.append(tr_curve[i] if i < len(tr_curve) else vl_curve[i])
            vl.append(vl_curve[i])
            p_sel = _staged_proba(algorithm, model, Xv_sel, i + 1) if len(sel) else np.array([])
            mean_abs = float(np.mean(np.abs(np.asarray(y_sel) - p_sel))) if len(y_sel) else 0.0
            state = {"kind": "resid", "round": i + 1, "total": n, "lib": algorithm,
                     "probs": [float(v) for v in p_sel], "y": list(y_sel),
                     "mean_abs": mean_abs}
            if progress_callback:
                progress_callback(j, len(idx), i + 1, f"Árvore {i + 1}/{n}",
                                  tr[-1], vl[-1], state)

        # Showcase: algumas árvores reais do comitê (início, meio, fim)
        if extra_callback is not None:
            try:
                show = sorted({0, n // 2, max(n - 1, 0)})
                trees = _extract_trees(algorithm, model, show, feat_names)
                for s_i, ti in enumerate(show, 1):
                    extra_callback(s_i, len(show),
                                   {"kind": "tree", "round": ti + 1, "total": n,
                                    "lib": algorithm, "nodes": trees.get(ti, [])})
            except Exception:
                pass

        return {"mode": "boosting", "x_label": "Árvores (rounds de boosting)",
                "steps": steps, "train": tr, "val": vl, "metric": "roc_auc"}

    # ── Demais modelos: curva por volume de dados ─────────────────────────────
    from sklearn.model_selection import train_test_split
    fracs = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0]
    steps, tr, vl = [], [], []
    for k, frac in enumerate(fracs, 1):
        n = max(30, int(len(X_tr) * frac))
        try:
            if frac < 1.0 and n < len(X_tr):
                Xs, _, ys, _ = train_test_split(
                    X_tr, y_tr, train_size=n, stratify=y_tr, random_state=42)
            else:
                Xs, ys = X_tr, y_tr
            fast = {"n_estimators": 80, "max_depth": 4}
            pipe = build_pipeline(Xs, algorithm, fast, balancing="none", treatment=treatment)
            pipe.fit(Xs, ys)
            ta = _safe_auc(ys, pipe.predict_proba(Xs)[:, 1])
            va = _safe_auc(y_val, pipe.predict_proba(X_val)[:, 1])
        except Exception:
            ta = va = 0.5
        steps.append(n); tr.append(ta); vl.append(va)
        if progress_callback:
            progress_callback(k, len(fracs), n, f"{int(frac * 100)}% ({n:,} amostras)", ta, va, None)
    return {"mode": "volume", "x_label": "Registros de treinamento",
            "steps": steps, "train": tr, "val": vl, "metric": "roc_auc"}
