"""
Preprocessing and cleaning for scraped app reviews.

Task 1 responsibilities:
- Deduplicate
- Handle missing values
- Normalize date format to YYYY-MM-DD
- Enforce Task 1 output schema: review, rating, date, bank, source
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

import pandas as pd

TASK1_COLUMNS: list[str] = ["review", "rating", "date", "bank", "source"]


def clean_reviews_task1(
    df_raw: pd.DataFrame,
    *,
    min_date: Optional[str] = None,
    max_date: Optional[str] = None,
    dedup_strategy: Literal["review_id",
                            "bank_review_date", "bank_review"] = "review_id",
) -> pd.DataFrame:
    """
    Clean raw scraped reviews into Task 1 deliverable format.

    Steps (recommended)
    -------------------
    1) Standardize column names (map google-play-scraper fields → project fields)
    2) Drop rows with missing critical fields: review, rating, date, bank
    3) Normalize date to YYYY-MM-DD
    4) Deduplicate using chosen strategy:
       - 'review_id' if present (best)
       - else fallback to ('bank', 'review', 'date')
    5) Enforce schema and types:
       - rating int in [1,5]
       - bank str in allowed codes
       - source constant 'Google Play'
    6) Return dataframe with EXACT columns:
       review, rating, date, bank, source

    Parameters
    ----------
    df_raw:
        Raw dataframe output of scraping module.
    min_date, max_date:
        Optional filters in YYYY-MM-DD.
    dedup_strategy:
        Defines how duplicates are removed.

    Returns
    -------
    pd.DataFrame
        Cleaned Task 1 dataframe with required columns.
    """
    if df_raw is None:
        raise ValueError("df_raw is None")

    df = df_raw.copy()

    # 1) Standardize column names (google-play-scraper -> project)
    rename_map = {
        "content": "review",
        "score": "rating",
        "at": "date",
        "reviewId": "review_id",
    }
    df = df.rename(columns=rename_map)

    # 2) Drop rows with missing critical fields
    required_cols = [c for c in ["review", "rating",
                                 "date", "bank"] if c in df.columns]
    missing_required = [c for c in ["review", "rating",
                                    "date", "bank"] if c not in df.columns]
    if missing_required:
        raise ValueError(
            f"Missing required columns in raw data: {missing_required}")

    df = df.dropna(subset=required_cols)

    # 3) Normalize date to YYYY-MM-DD
    df["date"] = pd.to_datetime(
        df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["date"])

    # 4) Coerce rating to int and keep valid range
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.dropna(subset=["rating"])
    df["rating"] = df["rating"].astype(int)
    df = df[df["rating"].between(1, 5)]

    # 5) Optional date filters
    if min_date is not None:
        min_date_dt = pd.to_datetime(min_date, errors="raise")
        df = df[pd.to_datetime(df["date"], errors="coerce") >= min_date_dt]
    if max_date is not None:
        max_date_dt = pd.to_datetime(max_date, errors="raise")
        df = df[pd.to_datetime(df["date"], errors="coerce") <= max_date_dt]

    # 6) Deduplicate
    if dedup_strategy == "review_id" and "review_id" in df.columns:
        df = df.drop_duplicates(subset=["review_id"], keep="first")
    elif dedup_strategy == "bank_review_date":
        df = df.drop_duplicates(
            subset=["bank", "review", "date"], keep="first")
    elif dedup_strategy == "bank_review":
        df = df.drop_duplicates(subset=["bank", "review"], keep="first")
    else:
        raise ValueError(
            "Invalid dedup_strategy. Use one of: 'review_id', 'bank_review_date', 'bank_review'."
        )

    # 7) Enforce schema: review, rating, date, bank, source
    if "source" not in df.columns:
        df["source"] = "Google Play"
    df = df[TASK1_COLUMNS].copy()

    # 8) Final missingness check
    if df.isna().any().any():
        raise ValueError("Cleaned dataframe still contains missing values")

    return df


def clean_reviews_csv_task1(
    *,
    in_csv: Path,
    out_csv: Path,
    dedup_strategy: str = "review_id",
) -> Path:
    """
    Load raw CSV, clean to Task 1 spec, and save to processed CSV.
    """
    df_raw = pd.read_csv(in_csv)
    df_clean = clean_reviews_task1(
        df_raw, dedup_strategy=dedup_strategy)  # type: ignore[arg-type]
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(out_csv, index=False)
    return out_csv
