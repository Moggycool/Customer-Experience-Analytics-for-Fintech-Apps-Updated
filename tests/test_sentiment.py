"""Tests for sentiment analysis functions.
"""
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from src.bank_reviews.nlp.sentiment import label_from_probs  # noqa: E402


def test_label_neutral_when_close_probs():
    """Test that when the positive and negative probabilities are close, 
       the label is NEUTRAL.
       Using a neutral_margin of 0.15, if the absolute difference between
       the positive and negative probabilities is less than 0.15, the label should be NEUTRAL.
    """
    # abs diff = 0.05 < 0.15 => NEUTRAL
    # abs diff = 0.10 < 0.15 => NEUTRAL
    assert label_from_probs(0.55, 0.45, neutral_margin=0.15) == "NEUTRAL"


def test_label_positive_when_diff_large():
    """Test that when the positive probability is much higher than the negative probability,
       the label is POSITIVE.
       Using a neutral_margin of 0.15, if the positive probability is at least 0.15 higher than the negative probability, the label should be POSITIVE.
    """
    assert label_from_probs(0.90, 0.10, neutral_margin=0.15) == "POSITIVE"


def test_label_negative_when_diff_large():
    """Test that when the negative probability is much higher than the positive probability,
       the label is NEGATIVE.
       Using a neutral_margin of 0.15, if the negative probability is at least 0.15 higher than the positive probability, the label should be NEGATIVE.
    """
    assert label_from_probs(0.10, 0.90, neutral_margin=0.15) == "NEGATIVE"
