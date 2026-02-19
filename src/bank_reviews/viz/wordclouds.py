"""
Wordcloud utilities for bank_reviews.

This module is intentionally optional: it requires the third-party `wordcloud`
package. If it is not installed, functions raise a clear RuntimeError.

Usage:
- make_wordcloud_for_bank(df, bank="CBE")
- make_wordcloud_grid(df)

Returns (fig, ax) / (fig, axes) for notebook use and saving.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class WordcloudStyle:
    """Styling options for wordclouds."""
    width: int = 900
    height: int = 450
    background_color: str = "white"
    max_words: int = 150
    colormap: str = "viridis"


def _import_wc():
    try:
        from wordcloud import WordCloud, STOPWORDS  # noqa: WPS433
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "wordcloud is not installed. Install it via: pip install wordcloud") from e

    import matplotlib.pyplot as plt  # noqa: WPS433

    return WordCloud, STOPWORDS, plt


def _ensure_cols(df: pd.DataFrame, cols: list[str], *, df_name: str = "df") -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing columns in {df_name}: {missing}. Found: {list(df.columns)}")


def make_wordcloud_for_bank(
    df_reviews: pd.DataFrame,
    *,
    bank: str,
    text_col: str = "review",
    bank_col: str = "bank",
    extra_stopwords: Optional[set[str]] = None,
    title: Optional[str] = None,
    style: WordcloudStyle = WordcloudStyle(),
):
    """Create a wordcloud for a single bank from raw review text."""
    _ensure_cols(df_reviews, [text_col, bank_col], df_name="df_reviews")

    WordCloud, STOPWORDS, plt = _import_wc()

    d = df_reviews[df_reviews[bank_col].astype(str) == str(bank)].copy()
    text = "\n".join(d[text_col].astype(str).tolist())

    stops = set(STOPWORDS)
    if extra_stopwords:
        stops |= set(map(str.lower, extra_stopwords))

    wc = WordCloud(
        width=style.width,
        height=style.height,
        background_color=style.background_color,
        max_words=style.max_words,
        stopwords=stops,
        colormap=style.colormap,
    ).generate(text)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(title or f"Wordcloud — {bank}")
    fig.tight_layout()
    return fig, ax


def make_wordcloud_grid(
    df_reviews: pd.DataFrame,
    *,
    text_col: str = "review",
    bank_col: str = "bank",
    extra_stopwords: Optional[set[str]] = None,
    style: WordcloudStyle = WordcloudStyle(),
):
    """Create a 1×N grid of wordclouds, one per bank."""
    _ensure_cols(df_reviews, [text_col, bank_col], df_name="df_reviews")

    WordCloud, STOPWORDS, plt = _import_wc()

    banks = sorted(df_reviews[bank_col].astype(str).unique().tolist())

    stops = set(STOPWORDS)
    if extra_stopwords:
        stops |= set(map(str.lower, extra_stopwords))

    n = len(banks)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4.5))
    if n == 1:
        axes = [axes]

    for ax, bank in zip(axes, banks):
        d = df_reviews[df_reviews[bank_col].astype(str) == str(bank)]
        text = "\n".join(d[text_col].astype(str).tolist())
        wc = WordCloud(
            width=style.width,
            height=style.height,
            background_color=style.background_color,
            max_words=style.max_words,
            stopwords=stops,
            colormap=style.colormap,
        ).generate(text)
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        ax.set_title(str(bank))

    fig.suptitle("Wordclouds by bank", y=1.02)
    fig.tight_layout()
    return fig, axes
