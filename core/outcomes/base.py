from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class OutcomeConfig(ABC):
    """Base class for all predictive outcomes.

    Subclasses implement the three abstract methods that define:
    - how to build the cohort from raw DataSUS data
    - how to engineer features from the cohort
    - which column is the target variable
    """

    key: str                          # unique identifier (used in session_state)
    name: str                         # display name
    description: str                  # one-paragraph description
    data_sources: list[str]           # e.g. ['SIH', 'SIM']
    observation_window_days: int      # look-back window for features
    prediction_window_days: int       # look-ahead window for outcome
    requires_linkage: bool            # whether inter-system record linkage is needed
    suggested_features: list[str]     # default feature columns
    target_col: str = "target"        # name of the binary target column
    icon: str = "🏥"
    estimated_download_min: int = 5   # rough estimate for the UI

    # ── Abstract interface ─────────────────────────────────────────────────────

    @abstractmethod
    def build_cohort(self, data: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Transform raw DataSUS tables into a flat cohort with one row per index event.

        Args:
            data: dict mapping source name ('SIH', 'SIM', ...) to preprocessed DataFrame.

        Returns:
            DataFrame with at least the columns in `suggested_features` + `target_col`.
        """

    @abstractmethod
    def build_features(self, cohort: pd.DataFrame) -> pd.DataFrame:
        """Apply feature engineering on the cohort (encoding, aggregations, etc.).

        Returns:
            DataFrame ready for ML training (numeric, no leakage).
        """

    @abstractmethod
    def get_target(self, cohort: pd.DataFrame) -> pd.Series:
        """Return the binary (0/1) target Series from the cohort."""

    # ── Helpers ────────────────────────────────────────────────────────────────

    def summary(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "data_sources": self.data_sources,
            "observation_window_days": self.observation_window_days,
            "prediction_window_days": self.prediction_window_days,
            "requires_linkage": self.requires_linkage,
        }
