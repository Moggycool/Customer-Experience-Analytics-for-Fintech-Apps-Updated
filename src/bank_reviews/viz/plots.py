"""
Visualization helpers for the bank_reviews project.

Design goals
------------
- Lightweight imports at module import time (CI friendly).
- Lazy-import matplotlib/seaborn only inside plotting functions.
- Functions accept DataFrames produced by Task-2 pipeline and notebook.
- Returns (fig, ax) for notebook display and for saving to disk.

Expected Task-2 tables:
- reviews_task2_scored.csv (row-level, with sentiment + themes)
- task2_sentiment_by_bank.csv
- task2_sentiment_by_bank_rating.csv
- task2_keywords_tfidf_by_bank.csv
- task2_theme_examples.csv

All plotting functions are deterministic (no randomness).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PlotStyle:
    """Centralized styling options."""

    style: str = "whitegrid"
    context: str = "notebook"
    palette: str = "Set2"
    dpi: int = 130


def _import_plotting():
    """Lazy import matplotlib/seaborn to keep base imports light."""
    import matplotlib.pyplot as plt  # noqa: WPS433
    import seaborn as sns  # noqa: WPS433

    return plt, sns


def _apply_style(style: PlotStyle):
    plt, sns = _import_plotting()
    sns.set_theme(style=style.style, context=style.context,
                  palette=style.palette)
    plt.rcParams["figure.dpi"] = style.dpi
    return plt, sns


def _ensure_columns(df: pd.DataFrame, cols: Iterable[str], *, df_name: str = "df") -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing columns in {df_name}: {missing}. Found: {list(df.columns)}")


def plot_sentiment_distribution(
    df_reviews: pd.DataFrame,
    *,
    bank_col: str = "bank",
    label_col: str = "sentiment_label",
    order: Optional[list[str]] = None,
    normalize: bool = True,
    title: str = "Sentiment distribution by bank",
    style: PlotStyle = PlotStyle(),
):
    """
    Stacked bar chart of sentiment label distribution by bank.

    If normalize=True, bars sum to 1.0 (shares). Otherwise counts.
    """
    _ensure_columns(df_reviews, [bank_col, label_col], df_name="df_reviews")
    plt, _ = _apply_style(style)

    tab = pd.crosstab(df_reviews[bank_col], df_reviews[label_col])
    if normalize:
        tab = tab.div(tab.sum(axis=1), axis=0)

    if order is None:
        order = list(tab.index)

    tab = tab.reindex(order)

    fig, ax = plt.subplots(figsize=(10, 4))
    bottom = np.zeros(len(tab), dtype=float)

    # stable label order (common SST-2 labels + NEUTRAL)
    preferred = ["NEGATIVE", "NEUTRAL", "POSITIVE"]
    label_order = [c for c in preferred if c in tab.columns] + \
        [c for c in tab.columns if c not in set(preferred)]

    for lab in label_order:
        vals = tab[lab].values
        ax.bar(tab.index, vals, bottom=bottom, label=lab)
        bottom = bottom + vals

    ax.set_title(title)
    ax.set_ylabel("Share" if normalize else "Count")
    ax.set_xlabel("Bank")
    ax.legend(title="Sentiment", bbox_to_anchor=(1.02, 1), loc="upper left")
    if normalize:
        ax.set_ylim(0, 1.0)

    fig.tight_layout()
    return fig, ax


def plot_sentiment_score_violin(
    df_reviews: pd.DataFrame,
    *,
    bank_col: str = "bank",
    score_col: str = "sentiment_score",
    title: str = "Sentiment score distribution by bank",
    style: PlotStyle = PlotStyle(),
):
    """Violin plot (with quartiles) of sentiment score by bank."""
    _ensure_columns(df_reviews, [bank_col, score_col], df_name="df_reviews")
    plt, sns = _apply_style(style)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.violinplot(data=df_reviews, x=bank_col, y=score_col,
                   inner="quartile", cut=0, ax=ax)
    ax.axhline(0, color="black", linewidth=1, alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel("Bank")
    ax.set_ylabel("Sentiment score (p_pos - p_neg)")
    fig.tight_layout()
    return fig, ax


def plot_mean_sentiment_by_bank(
    sent_by_bank: pd.DataFrame,
    *,
    bank_col: str = "bank",
    mean_col: str = "mean_sentiment_score",
    n_col: str = "n_reviews",
    title: str = "Mean sentiment by bank",
    style: PlotStyle = PlotStyle(),
):
    """Bar chart of mean sentiment per bank with optional n annotation."""
    _ensure_columns(sent_by_bank, [bank_col, mean_col], df_name="sent_by_bank")
    plt, sns = _apply_style(style)

    d = sent_by_bank.sort_values(mean_col, ascending=False).copy()
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=d, x=bank_col, y=mean_col, ax=ax)
    ax.axhline(0, color="black", linewidth=1, alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel("Bank")
    ax.set_ylabel("Mean sentiment score")

    if n_col in d.columns:
        for i, (_, row) in enumerate(d.iterrows()):
            ax.text(
                i, row[mean_col], f"n={int(row[n_col])}", ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    return fig, ax


def plot_sentiment_by_rating_heatmap(
    sent_by_bank_rating: pd.DataFrame,
    *,
    bank_col: str = "bank",
    rating_col: str = "rating",
    value_col: str = "mean_sentiment_score",
    title: str = "Mean sentiment by bank × rating",
    style: PlotStyle = PlotStyle(),
):
    """Heatmap of mean sentiment by bank and rating."""
    _ensure_columns(sent_by_bank_rating, [
                    bank_col, rating_col, value_col], df_name="sent_by_bank_rating")
    plt, sns = _apply_style(style)

    piv = sent_by_bank_rating.pivot_table(
        index=bank_col, columns=rating_col, values=value_col, aggfunc="mean")
    piv = piv.sort_index(axis=0).sort_index(axis=1)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    sns.heatmap(piv, annot=True, fmt=".2f", cmap="RdYlGn", center=0, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Rating")
    ax.set_ylabel("Bank")
    fig.tight_layout()
    return fig, ax


def plot_theme_counts_by_bank(
    df_reviews: pd.DataFrame,
    *,
    bank_col: str = "bank",
    theme_col: str = "theme_primary",
    top_n: int = 10,
    title: str = "Theme frequency by bank",
    style: PlotStyle = PlotStyle(),
):
    """Per-bank horizontal bars of theme counts (top_n)."""
    _ensure_columns(df_reviews, [bank_col, theme_col], df_name="df_reviews")
    plt, sns = _apply_style(style)

    d = df_reviews.dropna(subset=[theme_col]).copy()
    counts = d.groupby([bank_col, theme_col]).size().reset_index(name="n")

    banks = sorted(counts[bank_col].unique().tolist())
    nrows = len(banks)

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=1,
        figsize=(10, max(3, 2.6 * nrows)),
        sharex=False,
    )
    if nrows == 1:
        axes = [axes]

    for ax, bank in zip(axes, banks):
        sub = counts[counts[bank_col] == bank].sort_values(
            "n", ascending=False).head(top_n)
        sns.barplot(data=sub, y=theme_col, x="n", ax=ax)
        ax.set_title(f"{bank}")
        ax.set_xlabel("# reviews")
        ax.set_ylabel("Theme")

    fig.suptitle(title, y=1.02)
    fig.tight_layout()
    return fig, axes


def plot_top_keywords_by_bank(
    kw_by_bank: pd.DataFrame,
    *,
    bank_col: str = "bank",
    term_col: str = "term",
    score_col: str = "tfidf_score",
    top_k: int = 15,
    title: str = "Top TF-IDF keywords by bank",
    style: PlotStyle = PlotStyle(),
):
    """Per-bank horizontal bars of top TF-IDF terms."""
    _ensure_columns(kw_by_bank, [bank_col, term_col,
                    score_col], df_name="kw_by_bank")
    plt, sns = _apply_style(style)

    banks = sorted(kw_by_bank[bank_col].unique().tolist())
    nrows = len(banks)

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=1,
        figsize=(10, max(3, 2.9 * nrows)),
        sharex=False,
    )
    if nrows == 1:
        axes = [axes]

    for ax, bank in zip(axes, banks):
        sub = kw_by_bank[kw_by_bank[bank_col] == bank].sort_values(
            score_col, ascending=False).head(top_k)
        sns.barplot(data=sub, y=term_col, x=score_col, ax=ax)
        ax.set_title(f"{bank}")
        ax.set_xlabel("Mean TF-IDF")
        ax.set_ylabel("Term")

    fig.suptitle(title, y=1.02)
    fig.tight_layout()
    return fig, axes
