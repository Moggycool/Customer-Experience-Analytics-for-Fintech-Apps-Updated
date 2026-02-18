"""
Google Play Store scraping utilities.

Task 1 responsibilities:
- Collect reviews for each bank app via google-play-scraper
- Return a normalized raw dataframe (still may contain duplicates/missing)
- Persist raw CSV into data/raw/
"""

from __future__ import annotations


import sys
from pathlib import Path
from dataclasses import dataclass
import pandas as pd
from typing import Any, Dict, Iterable, Optional
from datetime import datetime


# Enable running this file directly (e.g. `python src/bank_reviews/scraping/play_store.py`)
# with the common `src/` project layout.
_SRC_DIR = Path(__file__).resolve().parents[2]
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# pylint: disable=import-error
from bank_reviews.config import AppConfig  # noqa: F401


@dataclass(frozen=True)
class ScrapeResult:
    """Result of a single-app scrape."""
    bank: str
    app_id: str
    n_requested: int
    n_scraped: int
    df: pd.DataFrame


def scrape_app_reviews(
    *,
    app_id: str,
    bank: str,
    source: str,
    lang: str = "en",
    country: str = "et",
    n_target: int = 450,
    sort: str = "NEWEST",
    sleep_seconds: float = 0.0,
    max_tries: int = 3,
) -> ScrapeResult:
    """
    Scrape Google Play reviews for a single app.

    Parameters
    ----------
    app_id:
        Google Play package name (e.g., 'com.combanketh.mobilebanking').
    bank:
        Short bank code used across the project (e.g., 'CBE', 'BOA', 'DASHEN').
    source:
        Source label to store in the dataset (e.g., 'Google Play').
    lang, country:
        google-play-scraper locale parameters.
    n_target:
        Target number of reviews to fetch (scrape slightly above minimum to survive cleaning).
    sort:
        Sorting mode; use 'NEWEST' for better temporal coverage consistency.
    sleep_seconds:
        Optional delay between pagination calls (politeness / stability).
    max_tries:
        Retries on transient errors.

    Returns
    -------
    ScrapeResult
        Includes a raw dataframe with at least:
        - review_id (if available from API)
        - review (text)
        - rating (int)
        - date (datetime or ISO string)
        - bank (str)
        - source (str)
        - app_id (str)
    """
    ...


def scrape_all_banks(
    *,
    app_cfg: AppConfig,
    n_target_per_bank: int = 450,
    sort: str = "NEWEST",
) -> pd.DataFrame:
    """
    Scrape reviews for all banks defined in AppConfig.

    Returns a concatenated raw dataframe (one row per review).
    Does NOT clean/deduplicate; cleaning is done in preprocessing module.
    """
    ...


def save_raw_reviews_csv(df: pd.DataFrame, out_csv: str) -> str:
    """
    Save raw scraped reviews to CSV.

    Keeps extra columns (review_id/app_id) useful for deduping and auditing.
    """
    ...
