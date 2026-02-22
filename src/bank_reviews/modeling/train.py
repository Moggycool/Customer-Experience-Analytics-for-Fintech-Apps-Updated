"""Training script for sentiment and theme classification models on bank reviews."""
from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any, cast

import pandas as pd
import psycopg
import joblib
from dotenv import load_dotenv

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score


load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")

TEXT_COL = "review_text"
SENT_COL = "sentiment_label"
THEME_COL = "theme_primary"


def fetch_training_data(limit: int | None = None) -> pd.DataFrame:
    """Fetch training data from the database, with optional row limit."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")

    lim_sql = f"LIMIT {int(limit)}" if limit else ""
    sql = f"""
    SELECT
        r.review_id,
        r.{TEXT_COL},
        r.{SENT_COL},
        r.{THEME_COL}
    FROM reviews r
    WHERE r.{TEXT_COL} IS NOT NULL
      AND r.{SENT_COL} IS NOT NULL
    {lim_sql}
    """

    with psycopg.connect(DATABASE_URL) as conn:
        df = pd.read_sql(sql, cast(Any, conn))

    df[TEXT_COL] = df[TEXT_COL].astype(str).str.strip()
    df = df[df[TEXT_COL].str.len() >= 3].copy()

    df[SENT_COL] = df[SENT_COL].astype(str).str.strip().str.lower()
    df[THEME_COL] = df[THEME_COL].astype(str).str.strip()

    # Turn empty strings into NA for theme
    df.loc[df[THEME_COL].isin(["", "nan", "None", "none"]), THEME_COL] = pd.NA
    return df


def make_text_clf() -> Pipeline:
    """Create a text classification pipeline with TF-IDF and Logistic Regression."""
    return Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                strip_accents="unicode",
                lowercase=True,
                sublinear_tf=True,
            )),
            ("clf", LogisticRegression(
                max_iter=3000,
                class_weight="balanced",
                # n_jobs not available for some solvers; keep default solver.
            )),
        ]
    )


def _train_one_task(
    X: pd.Series,
    y: pd.Series,
    task_name: str,
    out_path: Path,
) -> dict:
    """Train a text classification model for a specific task and save it."""
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = make_text_clf()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = float(accuracy_score(y_test, preds))

    print(f"\n[{task_name}] accuracy = {acc:.4f}")
    print(classification_report(y_test, preds))

    joblib.dump(model, out_path)

    return {
        "task": task_name,
        "accuracy": acc,
        "labels": sorted(y.unique().tolist()),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }


def train_and_save(model_dir: str = "models", limit: int | None = None) -> None:
    """Main function to train models and save them to disk."""
    out_dir = Path(model_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = fetch_training_data(limit=limit)

    # Sentiment
    sent_df = df.dropna(subset=[TEXT_COL, SENT_COL]).copy()
    sent_meta = _train_one_task(
        X=sent_df[TEXT_COL],
        y=sent_df[SENT_COL].astype(str),
        task_name="sentiment",
        out_path=out_dir / "sentiment.joblib",
    )

    # Theme (requires enough samples per class to stratify)
    theme_df = df.dropna(subset=[TEXT_COL, THEME_COL]).copy()

    # Filter very rare themes (prevents stratify errors + improves model stability)
    vc = theme_df[THEME_COL].value_counts()
    keep = vc[vc >= 10].index  # adjust threshold if needed
    theme_df = theme_df[theme_df[THEME_COL].isin(keep)].copy()

    if theme_df[THEME_COL].nunique() >= 2 and len(theme_df) >= 50:
        theme_meta = _train_one_task(
            X=theme_df[TEXT_COL],
            y=theme_df[THEME_COL].astype(str),
            task_name="theme",
            out_path=out_dir / "theme.joblib",
        )
    else:
        theme_meta = {
            "task": "theme",
            "skipped": True,
            "reason": "Not enough theme data after filtering (need >=2 classes and enough rows).",
            "n_rows_available": int(len(theme_df)),
            "n_unique_themes": int(theme_df[THEME_COL].nunique()),
        }
        print("\n[theme] skipped:", theme_meta["reason"])

    meta = {
        "text_col": TEXT_COL,
        "sentiment_col": SENT_COL,
        "theme_col": THEME_COL,
        "n_rows_total": int(len(df)),
        "sentiment": sent_meta,
        "theme": theme_meta,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"\nSaved to: {out_dir.resolve()}")
    print(" - sentiment.joblib")
    print(" - theme.joblib (if not skipped)")
    print(" - meta.json")


if __name__ == "__main__":
    train_and_save(model_dir="models", limit=None)
