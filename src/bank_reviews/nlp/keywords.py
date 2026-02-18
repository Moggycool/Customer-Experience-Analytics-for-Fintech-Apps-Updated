""" Keyword extraction using TF-IDF."""
# src/bank_reviews/nlp/keywords.py
from __future__ import annotations
import sys
from pathlib import Path

import pandas as pd

# Add project root (the folder that contains "src/") to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from bank_reviews.nlp.vectorize import TfidfConfig, fit_tfidf  # noqa: E402
from bank_reviews.utils.text import normalize_text  # noqa: E402


def top_keywords_by_bank(
    df: pd.DataFrame,
    *,
    text_col: str = "review",
    bank_col: str = "bank",
    cfg: TfidfConfig | None = None,
    top_k: int = 30,
) -> pd.DataFrame:
    """Get top keywords by bank using TF-IDF."""
    cfg = cfg or TfidfConfig()

    rows: list[dict] = []
    for bank, g in df.groupby(bank_col):
        texts = [normalize_text(x) for x in g[text_col].astype(str).tolist()]
        X, vec = fit_tfidf(texts, cfg)

        # Sum TF-IDF across docs -> bank-level importance
        bank_vec = X.sum(axis=0)  # 1 x n_features
        bank_vec = bank_vec.A1

        terms = vec.get_feature_names_out()
        if bank_vec.size == 0:
            continue

        top_idx = bank_vec.argsort()[::-1][:top_k]
        for i in top_idx:
            rows.append(
                {"bank": bank, "term": str(
                    terms[i]), "tfidf_score": float(bank_vec[i])}
            )

    return pd.DataFrame(rows).sort_values(["bank", "tfidf_score"], ascending=[True, False])
