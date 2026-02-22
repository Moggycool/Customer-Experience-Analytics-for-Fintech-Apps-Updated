""" Inference code for the bank reviews sentiment and theme classification models."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import joblib


@dataclass
class InferenceOutput:
    """Structured output for model inference results."""
    sentiment_label: str
    sentiment_score: float | None
    theme_primary: str | None
    theme_score: float | None


class TextInfer:
    """Class to load trained models and perform inference on review texts."""

    def __init__(self, model_dir: str = "models"):
        """Load the trained models from the specified directory."""
        p = Path(model_dir)
        self.sentiment = joblib.load(p / "sentiment.joblib")
        self.theme = joblib.load(
            p / "theme.joblib") if (p / "theme.joblib").exists() else None

    @staticmethod
    def _top_proba(model, text: str) -> float | None:
        """Get the top predicted probability from the model for the given text."""
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba([text])[0]
            return float(proba.max())
        return None

    def predict(self, text: str) -> InferenceOutput:
        """Predict the sentiment and theme for the given review text."""
        text = (text or "").strip()
        if not text:
            return InferenceOutput("error", None, None, None)

        sent = str(self.sentiment.predict([text])[0])
        sent_score = self._top_proba(self.sentiment, text)

        theme = None
        theme_score = None
        if self.theme is not None:
            theme = str(self.theme.predict([text])[0])
            theme_score = self._top_proba(self.theme, text)

        return InferenceOutput(sent, sent_score, theme, theme_score)
