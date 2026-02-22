"""
A bridge module to connect the Gradio dashboard to the prediction model.

This replaces the old rule-based baseline with the trained classical models:
- models/sentiment.joblib
- models/theme.joblib (optional but you have it)
Produced by: src.bank_reviews.modeling.train.py

Public API (kept stable):
- Prediction dataclass with .as_dict()
- load_predictor() -> Callable[[str], Prediction]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from functools import lru_cache

from src.bank_reviews.modeling.infer import TextInfer


@dataclass
class Prediction:
    """Structured prediction output for a review text."""
    sentiment_label: str
    sentiment_score: float | None = None
    theme_primary: str | None = None
    extra: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        """Convert the Prediction to a dictionary for JSON output."""
        d = {
            "sentiment_label": self.sentiment_label,
            "sentiment_score": self.sentiment_score,
            "theme_primary": self.theme_primary,
        }
        if self.extra:
            d.update(self.extra)
        return d


@lru_cache(maxsize=1)
def _infer() -> TextInfer:
    """
    Lazy-load and cache the inference models so Gradio doesn't reload them
    on every click.
    """
    # If your app runs from a different working directory,
    # you can change this to an absolute path or env var.
    return TextInfer(model_dir="models")


def load_predictor() -> Callable[[str], Prediction]:
    """
    Return a predictor callable compatible with the existing Gradio app code.

    Usage in app:
        predictor = load_predictor()
        pred = predictor(text)
        pred.as_dict()  # for gr.JSON
    """
    infer = _infer()

    def predict(text: str) -> Prediction:
        text = (text or "").strip()
        if not text:
            return Prediction(
                sentiment_label="error",
                extra={"error": "Empty input", "model_type": "tfidf_logreg"},
            )

        out = infer.predict(text)

        extra: dict[str, Any] = {
            "model_type": "tfidf_logreg",
        }

        # If your TextInfer returns theme_score as well, include it if present.
        # (Compatible with either version of infer.py.)
        theme_score = getattr(out, "theme_score", None)
        if theme_score is not None:
            extra["theme_score"] = theme_score

        return Prediction(
            sentiment_label=out.sentiment_label,
            sentiment_score=out.sentiment_score,
            theme_primary=out.theme_primary,
            extra=extra,
        )

    return predict
