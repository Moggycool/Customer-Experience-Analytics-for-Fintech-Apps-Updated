from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_sentiment_by_bank(df: pd.DataFrame, outpath: str) -> None:
    # stacked share bar
    ctab = (
        df.pivot_table(index="bank_name", columns="sentiment_label",
                       values="review_text", aggfunc="count", fill_value=0)
        .sort_index()
    )
    share = ctab.div(ctab.sum(axis=1), axis=0)

    ax = share[["NEGATIVE", "NEUTRAL", "POSITIVE"]].plot(
        kind="bar", stacked=True, figsize=(9, 5))
    ax.set_title("Sentiment distribution by bank (share of reviews)")
    ax.set_xlabel("Bank")
    ax.set_ylabel("Share")
    ax.legend(title="Sentiment", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()


def plot_rating_distribution(df: pd.DataFrame, outpath: str) -> None:
    plt.figure(figsize=(9, 5))
    sns.violinplot(data=df, x="bank_name", y="rating", inner="quartile", cut=0)
    sns.stripplot(data=df.sample(min(len(df), 800), random_state=7),
                  x="bank_name", y="rating", color="k", alpha=0.25, size=2)
    plt.title("Rating distribution by bank")
    plt.xlabel("Bank")
    plt.ylabel("Rating (1–5)")
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()


def plot_negative_trend_monthly(df: pd.DataFrame, outpath: str) -> None:
    # requires review_date
    d = df.dropna(subset=["review_date"]).copy()
    d["month"] = pd.to_datetime(
        d["review_date"]).dt.to_period("M").dt.to_timestamp()
    d["is_negative"] = (d["sentiment_label"] == "NEGATIVE").astype(int)

    g = d.groupby(["bank_name", "month"], as_index=False).agg(
        n=("is_negative", "size"),
        neg_share=("is_negative", "mean"),
        avg_rating=("rating", "mean"),
    )
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=g, x="month", y="neg_share", hue="bank_name", marker="o")
    plt.title("Monthly negative sentiment share (trend)")
    plt.xlabel("Month")
    plt.ylabel("Negative share")
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()


def plot_top_negative_keywords(df: pd.DataFrame, outpath: str, bank_name: str | None = None, topn: int = 15) -> None:
    # simple token frequency (interpretable bar; avoids wordcloud dependency)
    import re
    from collections import Counter

    d = df.copy()
    if bank_name:
        d = d[d["bank_name"] == bank_name]
    d = d[d["sentiment_label"] == "NEGATIVE"].copy()

    text = " ".join(d["review_text"].fillna("").astype(str).tolist()).lower()
    tokens = re.findall(r"[a-z]{3,}", text)
    stop = set(["the", "and", "for", "you", "your", "with", "this", "that", "have",
               "not", "but", "are", "was", "were", "from", "they", "them", "app", "bank"])
    tokens = [t for t in tokens if t not in stop]
    counts = Counter(tokens).most_common(topn)

    if not counts:
        return

    words, vals = zip(*counts)
    plt.figure(figsize=(9, 5))
    sns.barplot(x=list(vals), y=list(words), color="#4c72b0")
    title = "Top complaint keywords (NEGATIVE reviews)"
    if bank_name:
        title += f" — {bank_name}"
    plt.title(title)
    plt.xlabel("Count")
    plt.ylabel("Keyword")
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()
