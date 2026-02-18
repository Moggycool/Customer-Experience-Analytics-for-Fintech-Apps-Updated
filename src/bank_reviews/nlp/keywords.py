# src/bank_reviews/nlp/keywords.py
from __future__ import annotations

import pandas as pd

from bank_reviews.nlp.vectorize import TfidfConfig, fit_tfidf
from bank_reviews.utils.text import normalize_text


def top_keywords_by_bank(
    df: pd.DataFrame,
    *,
    text_col: str = "review",
    bank_col: str = "bank",
    cfg: TfidfConfig | None = None,
    top_k: int = 30,
) -> pd.DataFrame:
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
