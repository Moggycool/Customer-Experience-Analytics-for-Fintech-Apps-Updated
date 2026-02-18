"""
Date parsing utilities.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Any, Optional

import pandas as pd


def normalize_date(value: Any) -> Optional[str]:
    """
    Convert various date inputs to 'YYYY-MM-DD' string.

    Accepts:
    - datetime/date objects
    - pandas Timestamp
    - ISO-like strings

    Returns None if parsing fails.
    """
    try:
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, pd.Timestamp):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, str):
            dt = pd.to_datetime(value, errors="coerce")
            if pd.isna(dt):
                return None
            return dt.strftime("%Y-%m-%d")
    except Exception:
        return None
