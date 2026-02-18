""" Sentiment analysis using Hugging Face transformers."""
# src/bank_reviews/nlp/sentiment.py
from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

from bank_reviews.utils.text import normalize_text


@dataclass(frozen=True)
class SentimentConfig:
    """Configuration for sentiment analysis."""
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
    neutral_margin: float = 0.15
    batch_size: int = 32
    device: int = -1  # -1 CPU, 0 GPU


def label_from_probs(p_pos: float, p_neg: float, neutral_margin: float) -> str:
    """Determine sentiment label from positive and negative probabilities."""
    if abs(p_pos - p_neg) < neutral_margin:
        return "NEUTRAL"
    return "POSITIVE" if p_pos > p_neg else "NEGATIVE"


def add_sentiment_columns(df: pd.DataFrame, cfg: SentimentConfig) -> pd.DataFrame:
    """Add sentiment analysis columns to the DataFrame."""
    # Lazy import so CI can run without transformers/torch installed
    from transformers import pipeline

    if "review" not in df.columns:
        raise ValueError("Expected column 'review'")

    clf = pipeline(
        "sentiment-analysis",
        model=cfg.model_name,
        device=cfg.device,
        top_k=None,
    )  # type: ignore

    texts = df["review"].astype(str).map(normalize_text).tolist()

    p_pos_list: list[float] = []
    p_neg_list: list[float] = []
    labels: list[str] = []
    scores: list[float] = []

    for i in range(0, len(texts), cfg.batch_size):
        batch = texts[i: i + cfg.batch_size]
        results = clf(batch)

        for r in results:
            score_map = {x["label"].upper(): float(x["score"]) for x in r}
            p_pos = score_map.get("POSITIVE", 0.0)
            p_neg = score_map.get("NEGATIVE", 0.0)

            lab = label_from_probs(p_pos, p_neg, cfg.neutral_margin)
            sentiment_score = p_pos - p_neg

            p_pos_list.append(p_pos)
            p_neg_list.append(p_neg)
            labels.append(lab)
            scores.append(sentiment_score)

    out = df.copy()
    out["p_pos"] = p_pos_list
    out["p_neg"] = p_neg_list
    out["sentiment_score"] = scores
    out["sentiment_label"] = labels
    return out
