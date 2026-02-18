"""Tests for scenario generation functions in bank_reviews.analysis.scenarios.
"""

import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from src.bank_reviews.analysis.scenarios import sample_theme_examples  # noqa: E402


def test_sample_theme_examples_columns():
    """Test that sample_theme_examples returns a dataframe with the expected columns."""
    df = pd.DataFrame(
        {
            "bank": ["CBE", "CBE", "BOA"],
            "theme_primary": ["ACCESS_AUTH", "ACCESS_AUTH", "TXN_RELIABILITY"],
            "rating": [1, 2, 1],
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "sentiment_label": ["NEGATIVE", "NEGATIVE", "NEGATIVE"],
            "review": ["login error", "otp fail", "transfer failed"],
        }
    )
    out = sample_theme_examples(df, n_per_theme=1)
    assert set(out.columns) == {"bank", "theme",
                                "rating", "date", "sentiment_label", "review"}
