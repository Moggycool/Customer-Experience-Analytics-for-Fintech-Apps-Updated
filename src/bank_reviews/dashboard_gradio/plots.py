"""Plotting functions for the bank reviews dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px


def line_metric_over_time(df: pd.DataFrame, metric: str):
    """Plot a line chart of the given metric over time, broken down by bank."""
    if df is None or df.empty:
        return px.scatter(title="No data for selected filters")

    mapping = {
        "Negative share": ("neg_share", True),
        "Positive share": ("pos_share", True),
        "Avg rating": ("avg_rating", False),
        "Review volume": ("n_reviews", False),
        "Avg sentiment score": ("avg_sentiment_score", False),
    }
    y, is_share = mapping[metric]

    fig = px.line(
        df,
        x="month",
        y=y,
        color="bank_name",
        markers=True,
        title=f"{metric} over time",
    )
    if is_share:
        fig.update_yaxes(tickformat=".0%")
    return fig


def stacked_theme_sentiment(df: pd.DataFrame):
    """Plot a stacked bar chart of theme volume by sentiment."""
    if df is None or df.empty:
        return px.scatter(title="No data for selected filters")

    fig = px.bar(
        df,
        x="theme_primary",
        y="n_reviews",
        color="sentiment_label",
        barmode="stack",
        title="Theme volume by sentiment",
    )
    fig.update_layout(xaxis_title="Theme", yaxis_title="# Reviews")
    return fig
