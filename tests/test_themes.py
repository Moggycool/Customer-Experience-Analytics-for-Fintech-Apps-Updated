
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from src.bank_reviews.nlp.themes import ThemeConfig, assign_themes  # noqa: E402


def test_theme_access_auth():
    """Test that access/authentication related issues are correctly assigned 
       to the ACCESS_AUTH theme.
    """
    cfg = ThemeConfig(threshold=1.0, allow_multilabel=True, max_themes=2)
    primary, themes = assign_themes("Login error and OTP not working", cfg)
    assert primary == "ACCESS_AUTH"
    assert "ACCESS_AUTH" in themes


def test_theme_txn_reliability():
    """Test that transaction reliability issues are correctly assigned to 
       the TXN_RELIABILITY theme.
    """
    cfg = ThemeConfig(threshold=1.0, allow_multilabel=True, max_themes=2)
    primary, themes = assign_themes(
        "Transfer failed, pending transaction for hours", cfg)
    assert primary == "TXN_RELIABILITY"
    assert "TXN_RELIABILITY" in themes


def test_theme_other_when_below_threshold():
    """Test that reviews that do not meet the threshold for any theme are
       assigned to OTHER.
    """
    cfg = ThemeConfig(threshold=5.0, allow_multilabel=True, max_themes=2)
    primary, themes = assign_themes("Nice", cfg)
    assert primary == "OTHER"
    assert themes == "OTHER"


def test_theme_multilabel_up_to_2():
    """Test that when allow_multilabel is True, we can get up to 2 themes assigned.
    """
    cfg = ThemeConfig(threshold=1.0, allow_multilabel=True, max_themes=2)
    primary, themes = assign_themes(
        "Transfer failed and app keeps crashing after update", cfg)
    assert primary in {"TXN_RELIABILITY", "STABILITY_BUGS"}
    assert len(themes.split("|")) <= 2
