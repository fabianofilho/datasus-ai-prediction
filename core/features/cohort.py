"""CohortBuilder — constructs train/test-ready cohort from an OutcomeConfig.

Usage:
    builder = CohortBuilder(outcome_config)
    cohort  = builder.build(raw_data)         # full cohort DataFrame
    X, y    = builder.get_Xy(cohort)          # features + target
"""

from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split

from core.outcomes.base import OutcomeConfig


class CohortBuilder:
    def __init__(self, outcome: OutcomeConfig):
        self.outcome = outcome

    def build(self, raw_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Build the cohort from raw DataSUS data."""
        cohort = self.outcome.build_cohort(raw_data)
        cohort = self.outcome.build_features(cohort)
        return cohort

    def get_Xy(
        self,
        cohort: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """Return feature matrix X and target vector y."""
        y = self.outcome.get_target(cohort)

        # Only use suggested_features that are present in the cohort
        feature_cols = [
            c for c in self.outcome.suggested_features if c in cohort.columns
        ]
        # If none match, use all numeric columns except target
        if not feature_cols:
            feature_cols = [
                c for c in cohort.select_dtypes(include="number").columns
                if c != self.outcome.target_col
            ]

        X = cohort[feature_cols].copy()
        return X, y

    def split(
        self,
        cohort: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Return X_train, X_test, y_train, y_test."""
        X, y = self.get_Xy(cohort)
        return train_test_split(X, y, test_size=test_size, stratify=y, random_state=random_state)

    def class_balance(self, cohort: pd.DataFrame) -> dict:
        y = self.outcome.get_target(cohort)
        counts = y.value_counts()
        return {
            "total": len(y),
            "positive": int(counts.get(1, 0)),
            "negative": int(counts.get(0, 0)),
            "prevalence": float(counts.get(1, 0) / len(y)) if len(y) > 0 else 0.0,
        }
