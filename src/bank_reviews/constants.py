from __future__ import annotations

# Data targets
MIN_REVIEWS_PER_BANK: int = 400
SCRAPE_TARGET_PER_BANK: int = 450  # scrape a bit more to survive dedup/filters

# Sentiment (BERT + neutral band)
NEUTRAL_MARGIN: float = 0.15
BERT_BATCH_SIZE: int = 32

# Text processing
TFIDF_MAX_FEATURES: int = 5000
TFIDF_MIN_DF: int = 2
TFIDF_NGRAM_RANGE: tuple[int, int] = (1, 2)

# Columns (rubric + enriched)
RUBRIC_COLUMNS: list[str] = ["review", "rating", "date", "bank", "source"]

ENRICHED_COLUMNS: list[str] = [
    "review_id",
    "review",
    "rating",
    "date",
    "bank",
    "source",
    "lang",
    "sentiment_label",
    "sentiment_score",
    "sentiment_method",
    "theme",
]
