"""Tests for utility functions in bank_reviews.utils.text.
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from src.bank_reviews.utils.text import make_review_id, normalize_text, simple_clean_for_matching  # noqa: E402


def test_normalize_text_basic():
    """Test that normalize_text lowercases and collapses whitespace."""
    assert normalize_text("  Hello   World  ") == "hello world"


def test_simple_clean_for_matching_removes_punct():
    """Test that simple_clean_for_matching removes punctuation and lowercases."""
    assert simple_clean_for_matching(
        "Login error!!! OTP??") == "login error otp"


def test_make_review_id_deterministic():
    """Test that make_review_id produces the same ID for the same input."""
    a = make_review_id(
        review="App crashes often",
        bank="CBE",
        source="google_play",
        date="2024-01-01",
        rating=1,
    )
    b = make_review_id(
        review="App crashes often",
        bank="CBE",
        source="google_play",
        date="2024-01-01",
        rating=1,
    )
    assert a == b


def test_make_review_id_changes_when_review_changes():
    """Test that make_review_id produces different IDs for different reviews."""
    a = make_review_id(
        review="App crashes often",
        bank="CBE",
        source="google_play",
        date="2024-01-01",
        rating=1,
    )
    b = make_review_id(
        review="App works fine",
        bank="CBE",
        source="google_play",
        date="2024-01-01",
        rating=1,
    )
    assert a != b
