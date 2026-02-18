# src/bank_reviews/utils/text.py
from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Iterable

_WS_RE = re.compile(r"\s+")
_NON_WORD_RE = re.compile(r"[^\w\s]+", flags=re.UNICODE)


def normalize_text(s: str) -> str:
    """Light normalization safe for English app reviews."""
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u200b", "")  # zero-width space
    s = s.strip().lower()
    s = _WS_RE.sub(" ", s)
    return s


def simple_clean_for_matching(s: str) -> str:
    """
    Cleaning for rule-based matching (themes).
    Keeps whitespace; removes punctuation-ish noise.
    """
    s = normalize_text(s)
    s = _NON_WORD_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def make_review_id(
    *,
    review: str,
    bank: str,
    source: str,
    date: str,
    rating: int | str,
) -> str:
    """
    Deterministic hash id based on cleaned fields.
    """
    base = "||".join([
        normalize_text(bank),
        normalize_text(source),
        normalize_text(date),
        str(rating).strip(),
        normalize_text(review),
    ])
    return hashlib.sha1(base.encode("utf-8")).hexdigest()


def join_top_items(items: Iterable[str], top_k: int = 5, sep: str = "|") -> str:
    out = []
    for x in items:
        x = normalize_text(x)
        if x and x not in out:
            out.append(x)
        if len(out) >= top_k:
            break
    return sep.join(out)
