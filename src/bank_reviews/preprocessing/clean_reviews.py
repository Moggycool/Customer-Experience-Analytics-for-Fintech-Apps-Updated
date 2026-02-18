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
    ...


def clean_reviews_csv_task1(
    *,
    in_csv: Path,
    out_csv: Path,
    dedup_strategy: str = "review_id",
) -> Path:
    """
    Load raw CSV, clean to Task 1 spec, and save to processed CSV.
    """
    ...
