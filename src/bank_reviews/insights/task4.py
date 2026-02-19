from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional
import re

import pandas as pd


SentLabel = Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]


NEG_HINTS = [
    r"\bcrash(es|ed|ing)?\b", r"\berror(s)?\b", r"\bb(u)?g(s)?\b",
    r"\blogin\b", r"\bsign\s?in\b", r"\botp\b", r"\bpin\b",
    r"\bslow\b", r"\blag(gy)?\b", r"\bfreeze\b",
    r"\bnetwork\b", r"\bconnection\b", r"\btimeout\b",
    r"\bfailed\b", r"\bnot\s+working\b", r"\bstuck\b",
    r"\bupdate\b", r"\binstall\b",
]
POS_HINTS = [
    r"\bfast\b", r"\beasy\b", r"\bsmooth\b", r"\bquick\b",
    r"\bconvenient\b", r"\bgood\b", r"\bgreat\b", r"\bexcellent\b",
    r"\bworks\b", r"\breliable\b",
]


def _normalize_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def add_keyword_flags(df: pd.DataFrame, text_col: str = "review_text") -> pd.DataFrame:
    out = df.copy()
    txt = out[text_col].fillna("").map(_normalize_text)

    def has_any(patterns):
        rx = re.compile("|".join(patterns), flags=re.IGNORECASE)
        return txt.str.contains(rx)

    out["flag_neg_keyword"] = has_any(NEG_HINTS)
    out["flag_pos_keyword"] = has_any(POS_HINTS)
    return out


@dataclass
class ThemeInsight:
    bank_name: str
    kind: Literal["driver", "pain_point"]
    theme: str
    n: int
    share_within_bank: float
    pct_positive: float
    pct_negative: float
    avg_rating: float


def theme_summary_by_bank(
    reviews: pd.DataFrame,
    bank_col: str = "bank_name",
    theme_col: str = "theme_primary",
    sent_col: str = "sentiment_label",
    rating_col: str = "rating",
    min_n: int = 15,
) -> pd.DataFrame:
    df = reviews.copy()
    df[theme_col] = df[theme_col].fillna("UNKNOWN")
    df[sent_col] = df[sent_col].fillna("UNKNOWN")

    g = df.groupby([bank_col, theme_col], dropna=False)

    out = g.agg(
        n=(theme_col, "size"),
        avg_rating=(rating_col, "mean"),
        pct_positive=(sent_col, lambda x: (x == "POSITIVE").mean()),
        pct_negative=(sent_col, lambda x: (x == "NEGATIVE").mean()),
    ).reset_index()

    # within-bank share
    bank_totals = df.groupby(bank_col).size().rename("bank_n").reset_index()
    out = out.merge(bank_totals, on=bank_col, how="left")
    out["share_within_bank"] = out["n"] / out["bank_n"]

    # filter tiny themes to avoid noise
    out = out[out["n"] >= min_n].copy()

    # helpful ranking score (transparent)
    out["driver_score"] = out["pct_positive"] * \
        out["avg_rating"] * out["share_within_bank"]
    out["pain_score"] = out["pct_negative"] * \
        (6 - out["avg_rating"]) * out["share_within_bank"]
    return out.sort_values([bank_col, "n"], ascending=[True, False])


def top_drivers_and_pain_points(
    theme_summary: pd.DataFrame,
    bank_col: str = "bank_name",
    theme_col: str = "theme_primary",
    k: int = 3,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    drivers = (
        theme_summary.sort_values(
            [bank_col, "driver_score"], ascending=[True, False])
        .groupby(bank_col)
        .head(k)
        .assign(kind="DRIVER")
    )
    pains = (
        theme_summary.sort_values(
            [bank_col, "pain_score"], ascending=[True, False])
        .groupby(bank_col)
        .head(k)
        .assign(kind="PAIN_POINT")
    )
    keep = [bank_col, theme_col, "n", "share_within_bank",
            "avg_rating", "pct_positive", "pct_negative", "kind"]
    return drivers[keep].reset_index(drop=True), pains[keep].reset_index(drop=True)


def sample_snippets(
    reviews: pd.DataFrame,
    bank_name: str,
    theme: str,
    *,
    bank_col: str = "bank_name",
    theme_col: str = "theme_primary",
    text_col: str = "review_text",
    sent_col: str = "sentiment_label",
    kind: Literal["DRIVER", "PAIN_POINT"],
    n_snips: int = 2,
    max_chars: int = 180,
) -> list[str]:
    df = reviews.copy()
    df = df[(df[bank_col] == bank_name) & (
        df[theme_col].fillna("UNKNOWN") == theme)].copy()
    if df.empty:
        return []

    if kind == "DRIVER":
        # not perfect; we'll instead filter POS if exists
        df = df.sort_values([sent_col], ascending=True)
        pos = df[df[sent_col] == "POSITIVE"]
        if not pos.empty:
            df = pos
    else:
        neg = df[df[sent_col] == "NEGATIVE"]
        if not neg.empty:
            df = neg

    # choose longer, more informative snippets
    df["len"] = df[text_col].fillna("").astype(str).str.len()
    df = df.sort_values("len", ascending=False).head(n_snips)

    snips = []
    for t in df[text_col].fillna("").astype(str).tolist():
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) > max_chars:
            t = t[: max_chars - 1] + "…"
        snips.append(t)
    return snips
