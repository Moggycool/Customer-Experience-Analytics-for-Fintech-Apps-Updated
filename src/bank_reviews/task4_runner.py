""" task4_runner.py"""
# src/bank_reviews/task4_runner.py
from __future__ import annotations
import sys
from pathlib import Path

import pandas as pd
import textwrap

from sqlalchemy import create_engine, text

# Add project root (the folder that contains "src/") to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))


from src.bank_reviews.insights.task4 import (
    theme_summary_by_bank,
    top_drivers_and_pain_points,
    sample_snippets,
)  # noqa: E402
from src.bank_reviews.viz.task4_plots import (
    plot_sentiment_by_bank,
    plot_rating_distribution,
    plot_negative_trend_monthly,
    plot_top_negative_keywords,
)  # noqa: E402

SQL_REVIEWS = """
SELECT
    b.bank_name,
    b.app_name,
    r.review_id,
    r.bank_id,
    r.review_text,
    r.rating,
    r.review_date,
    r.source,
    r.sentiment_label,
    r.sentiment_score,
    r.theme_primary,
    r.review_hash
FROM reviews r
JOIN banks b ON b.bank_id = r.bank_id
WHERE r.review_text IS NOT NULL
"""


def _db_engine_from_env():
    import os

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return create_engine(db_url)

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    pwd = os.getenv("DB_PASSWORD")
    if not all([name, user, pwd]):
        raise RuntimeError(
            "Set DATABASE_URL or DB_NAME/DB_USER/DB_PASSWORD (and optionally DB_HOST/DB_PORT).")

    return create_engine(f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}")


def load_reviews_from_db() -> pd.DataFrame:
    eng = _db_engine_from_env()
    with eng.connect() as conn:
        df = pd.read_sql(text(SQL_REVIEWS), conn)

    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["sentiment_label"] = df["sentiment_label"].fillna(
        "UNKNOWN").astype(str).str.upper()
    df["theme_primary"] = df["theme_primary"].fillna("UNKNOWN").astype(str)
    df["bank_name"] = df["bank_name"].astype(str)
    df["source"] = df["source"].fillna("UNKNOWN").astype(str)
    return df


def build_recommendations_from_pain_themes(pain_themes: list[str]) -> list[str]:
    """
    Deterministic, theme-driven recommendations.
    Adjust keyword matching to your theme taxonomy once you inspect theme_primary values.
    """
    recs: list[str] = []

    for th in pain_themes:
        t = (th or "").upper()

        if any(k in t for k in ["STABILITY", "BUG", "CRASH"]):
            recs.append(
                "Stability program: crash analytics, staged rollouts, automated regression testing, and rollback for faulty releases.")
        if any(k in t for k in ["LOGIN", "AUTH", "OTP", "PIN", "PASSWORD"]):
            recs.append(
                "Fix login/auth friction: improve OTP delivery reliability, add biometric login, and implement clear self-service recovery + error messages.")
        if any(k in t for k in ["PERFORMANCE", "SLOW", "LAG"]):
            recs.append(
                "Performance optimization: reduce app startup time, cache key screens, and improve network retry/backoff and timeout handling.")
        if any(k in t for k in ["TXN", "TRANSFER", "PAYMENT", "TRANSACTION"]):
            recs.append(
                "Transaction reliability: clearer failure reasons, better pending-state tracking, idempotent retries, and receipts/status history.")
        if any(k in t for k in ["UX", "UI", "NAV", "USABILITY"]):
            recs.append(
                "UX simplification: reduce steps for common actions, improve navigation labels, and add contextual help around failures.")

    # Ensure at least 2
    recs = list(dict.fromkeys(recs))
    if len(recs) < 2:
        recs.append(
            "Add in-app support: FAQs + guided troubleshooting for login/transfer issues, with escalation (ticket/chat) when unresolved.")
    if len(recs) < 2:
        recs.append(
            "Add operational monitoring KPIs: login success rate, crash-free sessions, and transaction success rate by app version and device.")
    return recs[:3]


def render_report(df: pd.DataFrame, drivers: pd.DataFrame, pains: pd.DataFrame, report_path: Path) -> None:
    bank_stats = (
        df.groupby("bank_name", as_index=False)
        .agg(
            n_reviews=("review_id", "count"),
            avg_rating=("rating", "mean"),
            neg_share=("sentiment_label", lambda s: (s == "NEGATIVE").mean()),
            pos_share=("sentiment_label", lambda s: (s == "POSITIVE").mean()),
        )
        .sort_values(["n_reviews"], ascending=False)
    )

    # Comparison highlight (simple, readable)
    worst_neg = bank_stats.sort_values("neg_share", ascending=False).head(1)
    best_rating = bank_stats.sort_values("avg_rating", ascending=False).head(1)

    figdir = "figures"

    lines: list[str] = []
    lines.append(
        "# Task 4 — Insights and Recommendations (Mobile Banking App Reviews)\n")

    lines.append("## 1. Executive Summary\n")
    lines.append(
        textwrap.dedent(
            f"""
            This report analyzes customer reviews for mobile banking apps using **ratings**, **sentiment** outputs, and **themes** (`theme_primary`).
            We identify **drivers** of positive experience and **pain points** behind negative sentiment for each bank, compare banks, and propose actionable improvements.

            **Dataset size:** {len(df):,} reviews (from PostgreSQL).
            """
        ).strip()
        + "\n"
    )
    if not worst_neg.empty and not best_rating.empty:
        lines.append(
            f"\n**Cross-bank snapshot:** Highest negative share: **{worst_neg.iloc[0]['bank_name']}** "
            f"({worst_neg.iloc[0]['neg_share']:.1%}). Highest average rating: **{best_rating.iloc[0]['bank_name']}** "
            f"({best_rating.iloc[0]['avg_rating']:.2f}).\n"
        )

    lines.append("\n## 2. Cross-bank comparison (KPIs)\n")
    lines.append(bank_stats.to_markdown(index=False))

    lines.append("\n\n## 3. Visualizations\n")
    lines.append(
        f"- `{figdir}/sentiment_by_bank.png` — Sentiment distribution by bank")
    lines.append(
        f"- `{figdir}/rating_distribution.png` — Rating distribution by bank")
    lines.append(
        f"- `{figdir}/negative_trend_monthly.png` — Monthly negative sentiment trend")
    lines.append(
        f"- `{figdir}/top_negative_keywords_overall.png` — Top complaint keywords (negative reviews)")

    lines.append("\n\n## 4. Bank-level insights and recommendations\n")
    banks = sorted(df["bank_name"].dropna().unique().tolist())

    for b in banks:
        lines.append(f"\n### {b}\n")

        dsub = drivers[drivers["bank_name"] == b].copy()
        psub = pains[pains["bank_name"] == b].copy()

        # Drivers
        lines.append("#### Drivers (2+)\n")
        if dsub.empty:
            lines.append(
                "_No driver themes met the minimum sample threshold. Consider lowering min_n._\n")
        else:
            lines.append(dsub.to_markdown(index=False))
            for _, row in dsub.iterrows():
                theme = row["theme_primary"]
                snips = sample_snippets(df, b, theme, kind="DRIVER", n_snips=2)
                if snips:
                    lines.append(f"\nEvidence snippets for **{theme}**:")
                    for s in snips:
                        lines.append(f"- “{s}”")

        # Pain points
        lines.append("\n#### Pain points (2+)\n")
        if psub.empty:
            lines.append(
                "_No pain themes met the minimum sample threshold. Consider lowering min_n._\n")
        else:
            lines.append(psub.to_markdown(index=False))
            for _, row in psub.iterrows():
                theme = row["theme_primary"]
                snips = sample_snippets(
                    df, b, theme, kind="PAIN_POINT", n_snips=2)
                if snips:
                    lines.append(f"\nEvidence snippets for **{theme}**:")
                    for s in snips:
                        lines.append(f"- “{s}”")

        # Recommendations (2+ per bank)
        pain_themes = psub["theme_primary"].tolist() if not psub.empty else []
        recs = build_recommendations_from_pain_themes(pain_themes)

        lines.append("\n#### Recommendations (2+)\n")
        for i, r in enumerate(recs, 1):
            lines.append(f"{i}. {r}")

        safe_b = b.lower().replace(" ", "_")
        lines.append(
            f"\nAdditional keywords figure: `{figdir}/top_negative_keywords_{safe_b}.png`")

    lines.append("\n\n## 5. Ethics and limitations\n")
    lines.append(
        textwrap.dedent(
            f"""
            - **Review selection bias:** Reviewers are self-selected; negative experiences are often overrepresented.
            - **Theme assignment limitations:** Automated theme extraction may misclassify or miss nuanced feedback.
            - **Sentiment model caveats:** Sentiment analysis may not fully capture sarcasm, mixed feelings, or context.
            - **Actionability:** Recommendations are based on theme keywords and may require further validation.

            **Dataset size:** {len(df):,} reviews (from PostgreSQL).
            """
        ).strip()
        + "\n"
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_task4(out_dir: str = "reports/task4", min_n: int = 15, top_k: int = 3) -> None:
    out = Path(out_dir)
    fig_dir = out / "figures"
    out.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = load_reviews_from_db()

    # Insight tables
    theme_sum = theme_summary_by_bank(
        df,
        bank_col="bank_name",
        theme_col="theme_primary",
        sent_col="sentiment_label",
        rating_col="rating",
        min_n=min_n,
    )
    drivers, pains = top_drivers_and_pain_points(
        theme_sum, bank_col="bank_name", theme_col="theme_primary", k=top_k)

    # Evidence exports
    theme_sum.to_csv(out / "theme_summary_by_bank.csv", index=False)
    drivers.to_csv(out / "top_drivers_by_bank.csv", index=False)
    pains.to_csv(out / "top_pain_points_by_bank.csv", index=False)

    # Plots (3–5)
    plot_sentiment_by_bank(df, str(fig_dir / "sentiment_by_bank.png"))
    plot_rating_distribution(df, str(fig_dir / "rating_distribution.png"))
    plot_negative_trend_monthly(
        df, str(fig_dir / "negative_trend_monthly.png"))
    plot_top_negative_keywords(
        df, str(fig_dir / "top_negative_keywords_overall.png"), bank_name=None)

    for b in sorted(df["bank_name"].dropna().unique()):
        safe_b = b.lower().replace(" ", "_")
        plot_top_negative_keywords(
            df, str(fig_dir / f"top_negative_keywords_{safe_b}.png"), bank_name=b)

    
    render_report(df, drivers, pains, out / "task4_report.md")

    print(f"[OK] Task 4 written to: {out.resolve()}")
