from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


def _make_review_hash(bank: str, review_text: str, review_date, rating, source: str) -> str:
    parts = [
        str(bank or "").strip().lower(),
        str(review_text or "").strip(),
        str(review_date or ""),
        str(rating or ""),
        str(source or "").strip().lower(),
    ]
    raw = "||".join(parts).encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()


def _parse_themes(cell) -> list[str]:
    if cell is None or (isinstance(cell, float) and pd.isna(cell)):
        return []
    s = str(cell).strip()
    if not s:
        return []
    if s.startswith("[") and s.endswith("]"):
        s2 = s.strip("[]").strip()
        if not s2:
            return []
        items = [x.strip().strip("'").strip('"') for x in s2.split(",")]
        return [t for t in items if t]
    if "|" in s:
        return [t.strip() for t in s.split("|") if t.strip()]
    if "," in s:
        return [t.strip() for t in s.split(",") if t.strip()]
    return [s]


def load_task1_clean_csv(
    engine: Engine,
    csv_path: str | Path,
    *,
    min_rows_required: int = 400,
) -> dict:
    """
    Task 1 columns:
      review,rating,date,bank,source
    We generate review_hash and insert base rows.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Task1 CSV not found: {csv_path.resolve()}")

    df = pd.read_csv(csv_path)

    required = {"bank", "review", "rating", "date", "source"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Task1 CSV missing columns: {sorted(missing)}. Found: {list(df.columns)}")

    df["review"] = df["review"].astype(str).str.strip()
    df = df[df["review"].str.len() > 0].copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

    if len(df) < min_rows_required:
        raise ValueError(
            f"Only {len(df)} rows in Task1; requirement is >= {min_rows_required}")

    df["review_hash"] = df.apply(
        lambda r: _make_review_hash(
            r["bank"], r["review"], r["date"], r["rating"], r["source"]),
        axis=1,
    )

    banks_df = (
        df[["bank"]]
        .dropna()
        .drop_duplicates()
        .rename(columns={"bank": "bank_name"})
        .sort_values("bank_name")
        .reset_index(drop=True)
    )

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO banks (bank_name)
                VALUES (:bank_name)
                ON CONFLICT (bank_name) DO NOTHING;
            """),
            banks_df.to_dict(orient="records"),
        )

        bank_map = dict(conn.execute(
            text("SELECT bank_name, bank_id FROM banks;")).all())
        df["bank_id"] = df["bank"].map(bank_map)
        df = df.dropna(subset=["bank_id"]).copy()
        df["bank_id"] = df["bank_id"].astype(int)

        payload = df[[
            "bank_id", "review", "rating", "date", "source", "review_hash"
        ]].rename(columns={
            "review": "review_text",
            "date": "review_date",
        }).to_dict(orient="records")

        res = conn.execute(
            text("""
                INSERT INTO reviews (
                    bank_id, review_text, rating, review_date, source, review_hash
                )
                VALUES (
                    :bank_id, :review_text, :rating, :review_date, :source, :review_hash
                )
                ON CONFLICT (review_hash) DO NOTHING;
            """),
            payload
        )

        total_reviews = conn.execute(
            text("SELECT COUNT(*) FROM reviews;")).scalar_one()

    return {
        "task1_rows": int(len(df)),
        "task1_insert_attempted": int(len(payload)),
        "task1_insert_rowcount_reported": int(res.rowcount) if res.rowcount is not None else None,
        "total_reviews_in_db": int(total_reviews),
    }


def update_from_task2_scored_csv(
    engine: Engine,
    csv_path: str | Path,
    *,
    load_theme_links: bool = True,
) -> dict:
    """
    Task 2 file columns include:
      review,rating,date,bank,source,review_id,p_pos,p_neg,sentiment_score,sentiment_label,theme_primary,themes

    We compute review_hash the same way and update by review_hash.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Task2 CSV not found: {csv_path.resolve()}")

    df = pd.read_csv(csv_path)

    required = {"bank", "review", "rating", "date", "source",
                "sentiment_score", "sentiment_label", "theme_primary", "themes"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Task2 scored CSV missing columns: {sorted(missing)}. Found: {list(df.columns)}")

    df["review"] = df["review"].astype(str).str.strip()
    df = df[df["review"].str.len() > 0].copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["review_hash"] = df.apply(
        lambda r: _make_review_hash(
            r["bank"], r["review"], r["date"], r["rating"], r["source"]),
        axis=1,
    )

    upd = df[["review_hash", "sentiment_score", "sentiment_label",
              "theme_primary"]].to_dict(orient="records")

    with engine.begin() as conn:
        res_upd = conn.execute(
            text("""
                UPDATE reviews r
                SET
                    sentiment_score = u.sentiment_score,
                    sentiment_label = u.sentiment_label,
                    theme_primary   = u.theme_primary
                FROM (
                    SELECT
                        :review_hash::text AS review_hash,
                        :sentiment_score::float8 AS sentiment_score,
                        :sentiment_label::text AS sentiment_label,
                        :theme_primary::text AS theme_primary
                ) AS u
                WHERE r.review_hash = u.review_hash;
            """),
            upd
        )

        # unmatched hashes (Task2 rows that didn't find a Task1 row)
        # (safe but can be slower for huge data; fine for your scale)
        missing_hashes = conn.execute(
            text("""
                SELECT COUNT(*) FROM (
                    SELECT :review_hash::text AS review_hash
                ) u
                LEFT JOIN reviews r ON r.review_hash = u.review_hash
                WHERE r.review_hash IS NULL;
            """),
            [{"review_hash": h} for h in df["review_hash"].tolist()]
        ).scalar_one()

        theme_links_inserted = 0
        themes_inserted = 0

        if load_theme_links:
            df["_themes_list"] = df["themes"].apply(_parse_themes)
            all_themes = sorted(
                {t for lst in df["_themes_list"] for t in lst if t})

            if all_themes:
                conn.execute(
                    text("""
                        INSERT INTO themes (theme_name)
                        VALUES (:theme_name)
                        ON CONFLICT (theme_name) DO NOTHING;
                    """),
                    [{"theme_name": t} for t in all_themes]
                )
                themes_inserted = len(all_themes)

                theme_map = dict(conn.execute(
                    text("SELECT theme_name, theme_id FROM themes;")).all())

                # map review_hash -> review_id (DB PK)
                rh_to_id = dict(conn.execute(
                    text("SELECT review_hash, review_id FROM reviews;")).all())

                links = []
                for rh, lst in zip(df["review_hash"].tolist(), df["_themes_list"].tolist()):
                    rid = rh_to_id.get(rh)
                    if rid is None:
                        continue
                    for t in lst:
                        tid = theme_map.get(t)
                        if tid is not None:
                            links.append(
                                {"review_id": int(rid), "theme_id": int(tid)})

                if links:
                    res_links = conn.execute(
                        text("""
                            INSERT INTO review_themes (review_id, theme_id)
                            VALUES (:review_id, :theme_id)
                            ON CONFLICT DO NOTHING;
                        """),
                        links
                    )
                    theme_links_inserted = int(
                        res_links.rowcount) if res_links.rowcount is not None else 0

        total = conn.execute(
            text("SELECT COUNT(*) FROM reviews;")).scalar_one()
        enriched = conn.execute(text("""
            SELECT COUNT(*) FROM reviews
            WHERE sentiment_label IS NOT NULL OR sentiment_score IS NOT NULL OR theme_primary IS NOT NULL;
        """)).scalar_one()

    return {
        "task2_rows": int(len(df)),
        "update_rowcount_reported": int(res_upd.rowcount) if res_upd.rowcount is not None else None,
        "task2_missing_hashes_in_db": int(missing_hashes),
        "themes_seen_insert_attempt": int(themes_inserted),
        "review_theme_links_inserted_rowcount_reported": int(theme_links_inserted),
        "total_reviews_in_db": int(total),
        "reviews_with_any_enrichment": int(enriched),
    }


def run_task3_pipeline_from_env(engine: Engine) -> dict:
    task1 = os.getenv("TASK1_CLEAN_CSV", "").strip()
    task2 = os.getenv("TASK2_SCORED_CSV", "").strip()
    if not task1 or not task2:
        raise RuntimeError(
            "Set TASK1_CLEAN_CSV and TASK2_SCORED_CSV in your .env")

    out1 = load_task1_clean_csv(engine, task1, min_rows_required=400)
    out2 = update_from_task2_scored_csv(engine, task2, load_theme_links=True)
    return {"task1_load": out1, "task2_update": out2}
