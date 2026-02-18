"""This module contains functions to compute various metrics and 
   aggregates from the reviews DataFrame.
"""
# src/bank_reviews/analysis/metrics.py
from __future__ import annotations
import pandas as pd


def sentiment_aggregates_by_bank(df: pd.DataFrame) -> pd.DataFrame:
    """Compute sentiment aggregates by bank."""
    g = df.groupby("bank", dropna=False)
    out = g.agg(
        n_reviews=("review", "size"),
        mean_sentiment_score=("sentiment_score", "mean"),
        pos_rate=("sentiment_label", lambda s: (s == "POSITIVE").mean()),
        neg_rate=("sentiment_label", lambda s: (s == "NEGATIVE").mean()),
        neutral_rate=("sentiment_label", lambda s: (s == "NEUTRAL").mean()),
    ).reset_index()
    return out.sort_values("bank")


def sentiment_aggregates_by_bank_rating(df: pd.DataFrame) -> pd.DataFrame:
    """Compute sentiment aggregates by bank and rating."""
    g = df.groupby(["bank", "rating"], dropna=False)
    out = g.agg(
        n_reviews=("review", "size"),
        mean_sentiment_score=("sentiment_score", "mean"),
        pos_rate=("sentiment_label", lambda s: (s == "POSITIVE").mean()),
        neg_rate=("sentiment_label", lambda s: (s == "NEGATIVE").mean()),
        neutral_rate=("sentiment_label", lambda s: (s == "NEUTRAL").mean()),
    ).reset_index()
    return out.sort_values(["bank", "rating"])
