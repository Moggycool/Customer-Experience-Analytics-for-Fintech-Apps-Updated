from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine


def count_reviews(engine: Engine) -> int:
    with engine.connect() as conn:
        return conn.execute(text("SELECT COUNT(*) FROM reviews;")).scalar_one()


def reviews_per_bank(engine: Engine) -> list[tuple[str, int]]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT b.bank_name, COUNT(*) AS n
            FROM reviews r
            JOIN banks b ON b.bank_id = r.bank_id
            GROUP BY b.bank_name
            ORDER BY n DESC;
        """)).all()
    return [(r[0], int(r[1])) for r in rows]


def avg_rating_per_bank(engine: Engine) -> list[tuple[str, float | None]]:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT b.bank_name, AVG(r.rating)::float8 AS avg_rating
            FROM reviews r
            JOIN banks b ON b.bank_id = r.bank_id
            GROUP BY b.bank_name
            ORDER BY avg_rating DESC NULLS LAST;
        """)).all()
    return [(r[0], (float(r[1]) if r[1] is not None else None)) for r in rows]
