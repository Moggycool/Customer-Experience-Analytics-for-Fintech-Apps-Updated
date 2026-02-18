"""This module contains functions to compute various metrics and
   aggregates from the reviews DataFrame.
"""
# src/bank_reviews/analysis/scenarios.py
from __future__ import annotations
import pandas as pd


def sample_theme_examples(
    df: pd.DataFrame,
    *,
    n_per_theme: int = 3,
) -> pd.DataFrame:
    """Sample examples for each theme."""
    cols = ["bank", "theme_primary", "rating",
            "date", "sentiment_label", "review"]
    d = df[cols].copy()
    return (
        d.groupby(["bank", "theme_primary"], dropna=False)
        .head(n_per_theme)
        .rename(columns={"theme_primary": "theme"})
        .reset_index(drop=True)
    )
