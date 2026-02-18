# src/bank_reviews/nlp/themes.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd

from bank_reviews.utils.text import simple_clean_for_matching


THEME_LEXICON: dict[str, dict[str, list[str]]] = {
    "ACCESS_AUTH": {
        "bigrams": ["login error", "sign in", "reset password", "wrong pin", "otp code", "verification code"],
        "unigrams": ["login", "signin", "password", "pin", "otp", "verify", "verification", "biometric", "fingerprint"],
    },
    "TXN_RELIABILITY": {
        "bigrams": ["slow transfer", "transfer failed", "payment failed", "transaction failed", "pending transaction", "money not received", "network error"],
        "unigrams": ["transfer", "transaction", "failed", "pending", "timeout", "reversal", "reversed", "declined", "delay", "slow"],
    },
    "STABILITY_BUGS": {
        "bigrams": ["keeps crashing", "app crashes", "after update", "not working"],
        "unigrams": ["crash", "crashes", "bug", "freeze", "stuck", "hang", "loading", "error", "update"],
    },
    "UX_UI": {
        "bigrams": ["user interface", "easy to use", "good ui", "bad ui"],
        "unigrams": ["ui", "ux", "interface", "design", "layout", "navigation", "simple", "confusing", "language"],
    },
    "SUPPORT_SERVICE": {
        "bigrams": ["customer service", "call center", "no response", "not helpful"],
        "unigrams": ["support", "service", "help", "agent", "branch", "complaint", "respond", "response"],
    },
}


@dataclass(frozen=True)
class ThemeConfig:
    unigram_weight: float = 1.0
    bigram_weight: float = 2.0
    threshold: float = 2.0
    allow_multilabel: bool = True
    max_themes: int = 2


def _count_hits(text: str, terms: list[str]) -> int:
    c = 0
    for t in terms:
        if t in text:
            c += 1
    return c


def score_themes(text: str, cfg: ThemeConfig) -> dict[str, float]:
    t = simple_clean_for_matching(text)
    scores: dict[str, float] = {}
    for theme, lex in THEME_LEXICON.items():
        bi = _count_hits(t, lex.get("bigrams", []))
        uni = _count_hits(t, lex.get("unigrams", []))
        scores[theme] = cfg.bigram_weight * bi + cfg.unigram_weight * uni
    return scores


def assign_themes(text: str, cfg: ThemeConfig) -> tuple[str, str]:
    scores = score_themes(text, cfg)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # primary
    primary, primary_score = ranked[0]
    if primary_score < cfg.threshold:
        return "OTHER", "OTHER"

    if not cfg.allow_multilabel:
        return primary, primary

    picked = [primary]
    for theme, sc in ranked[1:]:
        if len(picked) >= cfg.max_themes:
            break
        if sc >= cfg.threshold:
            picked.append(theme)

    themes = "|".join(picked)
    return primary, themes


def add_theme_columns(df: pd.DataFrame, cfg: ThemeConfig) -> pd.DataFrame:
    out = df.copy()
    primaries: list[str] = []
    multilabels: list[str] = []

    for txt in out["review"].astype(str).tolist():
        p, t = assign_themes(txt, cfg)
        primaries.append(p)
        multilabels.append(t)

    out["theme_primary"] = primaries
    out["themes"] = multilabels
    return out
