"""Shared feature engineering utilities."""

from __future__ import annotations

import pandas as pd
import numpy as np


def encode_categoricals(df: pd.DataFrame, cat_cols: list[str]) -> pd.DataFrame:
    """Label-encode categorical columns (safe with missing values)."""
    df = df.copy()
    for col in cat_cols:
        if col in df.columns:
            df[col] = pd.Categorical(df[col].astype(str)).codes.astype(float)
            df[col] = df[col].replace(-1, np.nan)
    return df


def icd10_chapter(series: pd.Series) -> pd.Series:
    """Extract ICD-10 chapter letter (first character) as a numeric code."""
    return pd.Categorical(series.astype(str).str[0].str.upper()).codes.astype(float)


def icd10_block(series: pd.Series) -> pd.Series:
    """Extract ICD-10 3-character block as a numeric code."""
    return pd.Categorical(series.astype(str).str[:3].str.upper()).codes.astype(float)


def age_group(age_series: pd.Series, bins=None, labels=None) -> pd.Series:
    """Convert continuous age to age-group categories (numeric codes)."""
    if bins is None:
        bins = [0, 1, 5, 18, 40, 60, 80, 120]
        labels = [0, 1, 2, 3, 4, 5, 6]
    return pd.cut(age_series, bins=bins, labels=labels, right=False).astype(float)


def flag_missing(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Add binary indicator columns for missingness."""
    df = df.copy()
    for col in cols:
        if col in df.columns:
            df[f"{col}_missing"] = df[col].isna().astype(int)
    return df


def clip_outliers(df: pd.DataFrame, col: str, lower_q=0.01, upper_q=0.99) -> pd.DataFrame:
    """Clip a column at quantile bounds."""
    df = df.copy()
    if col in df.columns:
        lo = df[col].quantile(lower_q)
        hi = df[col].quantile(upper_q)
        df[col] = df[col].clip(lo, hi)
    return df
