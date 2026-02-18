# src/bank_reviews/pipelines/task2_sentiment_themes.py
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

# Add the project root to sys.path so that bank_reviews can be imported
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.bank_reviews.analysis.metrics import (
    sentiment_aggregates_by_bank,
    sentiment_aggregates_by_bank_rating,
)  # noqa: E402
from src.bank_reviews.analysis.scenarios import sample_theme_examples  # noqa: E402
from src.bank_reviews.nlp.keywords import top_keywords_by_bank  # noqa: E402
from src.bank_reviews.nlp.sentiment import SentimentConfig, add_sentiment_columns  # noqa: E402
from src.bank_reviews.nlp.themes import ThemeConfig, add_theme_columns  # noqa: E402
from src.bank_reviews.utils.text import make_review_id  # noqa: E402


def run_task2(
    *,
    in_csv: Path,
    out_reviews_csv: Path,
    out_agg_bank_csv: Path,
    out_agg_bank_rating_csv: Path,
    out_keywords_csv: Path,
    out_examples_csv: Path,
) -> None:
    """Run the Task 2 pipeline: sentiment and theme analysis."""
    df = pd.read_csv(in_csv)

    # review_id
    df = df.copy()
    df["review_id"] = [
        make_review_id(
            review=r,
            bank=b,
            source=s,
            date=d,
            rating=rt,
        )
        for r, b, s, d, rt in zip(df["review"], df["bank"], df["source"], df["date"], df["rating"])
    ]

    # sentiment
    df = add_sentiment_columns(df, SentimentConfig())

    # themes
    df = add_theme_columns(df, ThemeConfig())

    # write review-level
    out_reviews_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_reviews_csv, index=False)

    # aggregates
    sentiment_aggregates_by_bank(df).to_csv(out_agg_bank_csv, index=False)
    sentiment_aggregates_by_bank_rating(df).to_csv(
        out_agg_bank_rating_csv, index=False)

    # keywords
    kw = top_keywords_by_bank(df, top_k=30)
    kw.to_csv(out_keywords_csv, index=False)

    # examples
    ex = sample_theme_examples(df, n_per_theme=3)
    ex.to_csv(out_examples_csv, index=False)
