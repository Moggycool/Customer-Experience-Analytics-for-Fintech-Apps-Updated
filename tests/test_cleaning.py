"""Tests for data cleaning and preprocessing functions.
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_task1_schema_expected_columns():
    """Test that the cleaned Task 1 dataframe has the expected columns."""
    df = pd.DataFrame(
        {
            "review": ["a"],
            "rating": [5],
            "date": ["2024-01-01"],
            "bank": ["CBE"],
            "source": ["google_play"],
        }
    )
    assert set(df.columns) == {"review", "rating", "date", "bank", "source"}
