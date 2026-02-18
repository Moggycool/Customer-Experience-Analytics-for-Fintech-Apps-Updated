# src/bank_reviews/nlp/vectorize.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass(frozen=True)
class TfidfConfig:
    ngram_range: tuple[int, int] = (1, 2)
    min_df: int = 3
    max_df: float = 0.9
    max_features: int | None = 20_000
    # keep simple; can later swap to spaCy stopwords
    stop_words: str | None = "english"
    lowercase: bool = True


def make_tfidf_vectorizer(cfg: TfidfConfig) -> TfidfVectorizer:
    return TfidfVectorizer(
        ngram_range=cfg.ngram_range,
        min_df=cfg.min_df,
        max_df=cfg.max_df,
        max_features=cfg.max_features,
        stop_words=cfg.stop_words,
        lowercase=cfg.lowercase,
    )


def fit_tfidf(texts: Sequence[str], cfg: TfidfConfig) -> tuple[np.ndarray, TfidfVectorizer]:
    vec = make_tfidf_vectorizer(cfg)
    X = vec.fit_transform(texts)
    return X, vec


def top_terms_from_tfidf_row(
    X_row,
    vectorizer: TfidfVectorizer,
    top_k: int = 10,
) -> list[tuple[str, float]]:
    """Extract top terms for a single document row vector."""
    if X_row.nnz == 0:
        return []
    inds = X_row.indices
    vals = X_row.data
    order = np.argsort(vals)[::-1][:top_k]
    feature_names = vectorizer.get_feature_names_out()
    return [(feature_names[inds[i]], float(vals[i])) for i in order]
