"""
IO helpers (CSV read/write, directory creation).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def ensure_parent_dir(path: Path) -> None:
    """Create parent directory if it doesn't exist."""
    parent_dir = path.parent
    parent_dir.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> pd.DataFrame:
    """Read CSV with safe defaults."""
    ...


def write_csv(df: pd.DataFrame, path: Path) -> Path:
    """Write dataframe to CSV (UTF-8) and return path."""
    ...


def validate_required_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    """Raise ValueError if required columns are missing."""
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
