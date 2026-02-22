"""Functions to compute impact scores for themes in bank reviews."""
from __future__ import annotations
import pandas as pd


def compute_priority_table(theme_df: pd.DataFrame) -> pd.DataFrame:
    """
    driver_score = (% positive) * (avg_rating) * (volume_share_of_theme)
    pain_score   = (% negative) * (6 - avg_rating) * (volume_share_of_theme)

    Expects theme_df columns:
      bank_name, theme_primary, sentiment_label, n_reviews, avg_rating
    """

    if theme_df is None or theme_df.empty:
        return pd.DataFrame()

    df = theme_df.copy()
    df["sentiment_label"] = df["sentiment_label"].astype(
        str).str.strip().str.lower()
    df["theme_primary"] = df["theme_primary"].astype(str).str.strip()

    df = theme_df.copy()

    bt_total = df.groupby(["bank_name", "theme_primary"], as_index=False).agg(
        bt_n=("n_reviews", "sum")
    )

    bank_total = bt_total.groupby("bank_name", as_index=False).agg(
        bank_n=("bt_n", "sum")
    )

    out = bt_total.merge(bank_total, on="bank_name", how="left")
    out["volume_share"] = out["bt_n"] / out["bank_n"].replace(0, pd.NA)

    # Weighted avg rating across sentiments
    tmp = df.copy()
    tmp["rating_x_n"] = tmp["avg_rating"] * tmp["n_reviews"]
    bt_rating = tmp.groupby(["bank_name", "theme_primary"], as_index=False).agg(
        rating_x_n=("rating_x_n", "sum"),
        bt_n=("n_reviews", "sum"),
    )
    bt_rating["avg_rating"] = bt_rating["rating_x_n"] / \
        bt_rating["bt_n"].replace(0, pd.NA)

    pos = df[df["sentiment_label"] == "POSITIVE"].groupby(
        ["bank_name", "theme_primary"], as_index=False
    ).agg(n_pos=("n_reviews", "sum"))
    neg = df[df["sentiment_label"] == "NEGATIVE"].groupby(
        ["bank_name", "theme_primary"], as_index=False
    ).agg(n_neg=("n_reviews", "sum"))

    out = out.merge(bt_rating[["bank_name", "theme_primary", "avg_rating"]], on=[
                    "bank_name", "theme_primary"], how="left")
    out = out.merge(pos, on=["bank_name", "theme_primary"], how="left")
    out = out.merge(neg, on=["bank_name", "theme_primary"], how="left")
    out[["n_pos", "n_neg"]] = out[["n_pos", "n_neg"]].fillna(0)

    out["pos_share"] = out["n_pos"] / out["bt_n"].replace(0, pd.NA)
    out["neg_share"] = out["n_neg"] / out["bt_n"].replace(0, pd.NA)

    out["driver_score"] = out["pos_share"] * \
        out["avg_rating"] * out["volume_share"]
    out["pain_score"] = out["neg_share"] * \
        (6 - out["avg_rating"]) * out["volume_share"]

    out = out[
        ["bank_name", "theme_primary", "bt_n", "volume_share", "avg_rating",
            "pos_share", "neg_share", "driver_score", "pain_score"]
    ].sort_values(["bank_name", "pain_score"], ascending=[True, False])

    return out
