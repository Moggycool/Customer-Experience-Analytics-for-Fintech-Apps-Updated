"""
Google Play Store scraping utilities.

Task 1 responsibilities:
- Collect reviews for each bank app via google-play-scraper
- Return a normalized raw dataframe (still may contain duplicates/missing)
- Persist raw CSV into data/raw/
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from dataclasses import dataclass

from typing import Optional

import pandas as pd


# Enable running this file directly (e.g. `python src/bank_reviews/scraping/play_store.py`)
# with the common `src/` project layout.
if __package__ in (None, ""):
    _SRC_DIR = Path(__file__).resolve().parents[2]
    if str(_SRC_DIR) not in sys.path:
        sys.path.insert(0, str(_SRC_DIR))

from bank_reviews.config import AppConfig


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
    try:
        from google_play_scraper import Sort, reviews  # type: ignore
    except ModuleNotFoundError as e:  # pragma: no cover
        raise ModuleNotFoundError(
            "google-play-scraper is not installed. Install `google-play-scraper` to enable scraping."
        ) from e

    sort_key = sort.strip().upper()
    sort_mode = Sort.NEWEST if sort_key == "NEWEST" else Sort.MOST_RELEVANT

    all_rows: list[dict] = []
    continuation_token = None

    while len(all_rows) < n_target:
        remaining = n_target - len(all_rows)
        count = min(200, remaining)

        last_error: Optional[BaseException] = None
        for attempt in range(max_tries):
            try:
                kwargs = {
                    "lang": lang,
                    "country": country,
                    "sort": sort_mode,
                    "count": count,
                }
                if continuation_token is not None:
                    kwargs["continuation_token"] = continuation_token

                rows, continuation_token = reviews(app_id, **kwargs)
                all_rows.extend(rows)
                last_error = None
                break
            except Exception as exc:  # pylint: disable=broad-exception-caught
                last_error = exc
                if attempt < max_tries - 1:
                    time.sleep(1.0 + attempt)
                    continue

        if last_error is not None:
            raise RuntimeError(
                f"Failed to scrape reviews for {bank} ({app_id}) after {max_tries} tries: {last_error}"
            )

        if continuation_token is None:
            break
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    df = pd.DataFrame(all_rows)

    # Normalize google-play-scraper field names -> project-friendly names
    if not df.empty:
        df = df.rename(
            columns={
                "reviewId": "review_id",
                "content": "review",
                "score": "rating",
                "at": "date",
            }
        )

    df["bank"] = bank
    df["source"] = source
    df["app_id"] = app_id

    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

    return ScrapeResult(
        bank=bank,
        app_id=app_id,
        n_requested=n_target,
        n_scraped=int(len(df)),
        df=df,
    )


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
    frames: list[pd.DataFrame] = []

    for bank_code, app_id in app_cfg.app_ids.items():
        res = scrape_app_reviews(
            app_id=app_id,
            bank=bank_code,
            source=app_cfg.source_name,
            lang=app_cfg.lang,
            country=app_cfg.country,
            n_target=n_target_per_bank,
            sort=sort,
        )
        frames.append(res.df)

    if not frames:
        return pd.DataFrame(
            columns=["review_id", "review", "rating",
                     "date", "bank", "source", "app_id"]
        )

    return pd.concat(frames, ignore_index=True)


def save_raw_reviews_csv(df: pd.DataFrame, out_csv: str) -> str:
    """
    Save raw scraped reviews to CSV.

    Keeps extra columns (review_id/app_id) useful for deduping and auditing.
    """
    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return str(out_path)


if __name__ == "__main__":  # pragma: no cover
    from bank_reviews.config import default_app_config

    cfg = default_app_config()
    df_raw = scrape_all_banks(app_cfg=cfg, n_target_per_bank=10)
    print(df_raw.head())
