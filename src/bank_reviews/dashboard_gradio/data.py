"""Data access and domain logic for the bank reviews dashboard."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Optional, cast

import pandas as pd
import psycopg
from dotenv import load_dotenv


# =========================
# Config
# =========================

@dataclass(frozen=True)
class DBConfig:
    """Database configuration from env."""
    conninfo: str

    @staticmethod
    def from_env(env_key: str = "DATABASE_URL") -> "DBConfig":
        """Load database config from environment variable."""
        load_dotenv()
        conninfo = os.environ.get(env_key)
        if conninfo:
            conninfo = conninfo.replace(
                "postgresql+psycopg2://", "postgresql://")
            conninfo = conninfo.replace(
                "postgresql+psycopg://", "postgresql://")
        if not conninfo:
            raise RuntimeError(
                f"Missing {env_key}. Set it to a PostgreSQL connection string like:\n"
                "postgresql://USER:PASSWORD@HOST:5432/DBNAME"
            )
        return DBConfig(conninfo=conninfo)


def connect(cfg: DBConfig):
    """Connect to the database."""
    return psycopg.connect(cfg.conninfo)


def read_sql_df(
    sql: str,
    params: Optional[dict[str, Any]] = None,
    cfg: Optional[DBConfig] = None,
) -> pd.DataFrame:
    """Run a SQL query and return a DataFrame."""
    cfg = cfg or DBConfig.from_env()
    with connect(cfg) as conn:
        return pd.read_sql_query(sql, cast(Any, conn), params=params)


# =========================
# Lightweight TTL cache
# =========================

class TTLCache:
    """A simple in-memory cache with TTL expiration."""

    def __init__(self, ttl_seconds: int = 60):
        self.ttl_seconds = ttl_seconds
        self._store: dict[tuple, tuple[float, Any]] = {}

    def get(self, key: tuple):
        item = self._store.get(key)
        if not item:
            return None
        ts, value = item
        if time.time() - ts > self.ttl_seconds:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: tuple, value: Any):
        self._store[key] = (time.time(), value)


_cache = TTLCache(ttl_seconds=int(os.environ.get("DASH_CACHE_TTL", "60")))


# =========================
# Helpers (normalization)
# =========================

def _as_optional_text(x: str) -> Optional[str]:
    """Convert UI dropdown values into optional text filters."""
    return None if x == "All" else x


# =========================
# Domain queries
# =========================

def get_filters(cfg: Optional[DBConfig] = None) -> dict[str, list[str]]:
    cfg = cfg or DBConfig.from_env()
    cached = _cache.get(("filters",))
    if cached is not None:
        return cached

    banks = read_sql_df(
        "select bank_name from banks order by bank_name", cfg=cfg
    )["bank_name"].tolist()

    sources = read_sql_df(
        "select distinct source from reviews where source is not null order by source", cfg=cfg
    )["source"].tolist()

    themes = read_sql_df(
        "select distinct theme_primary from reviews where theme_primary is not null order by theme_primary",
        cfg=cfg,
    )["theme_primary"].tolist()

    # Keep UI sentiment filters in lowercase; SQL normalizes DB values.
    out = {
        "banks": ["All"] + banks,
        "sources": ["All"] + sources,
        "themes": ["All"] + themes,
        "sentiments": ["All", "positive", "negative", "neutral"],
    }
    _cache.set(("filters",), out)
    return out


def monthly_summary(
    bank_name: str,
    source: str,
    theme: str,
    sentiment: str,
    start_date: str,
    end_date: str,
    cfg: Optional[DBConfig] = None,
) -> pd.DataFrame:
    """Monthly aggregates for exploration charts."""
    cfg = cfg or DBConfig.from_env()

    sql = """
    select
      date_trunc('month', r.review_date)::date as month,
      b.bank_name,
      count(*) as n_reviews,
      avg(r.rating)::float as avg_rating,
      avg(case when lower(trim(r.sentiment_label)) = 'negative' then 1 else 0 end)::float as neg_share,
      avg(case when lower(trim(r.sentiment_label)) = 'positive' then 1 else 0 end)::float as pos_share,
      avg(r.sentiment_score)::float as avg_sentiment_score
    from reviews r
    join banks b on b.bank_id = r.bank_id
    where (%(bank_name)s::text is null or b.bank_name = %(bank_name)s::text)
      and (%(source)s::text is null or r.source = %(source)s::text)
      and (%(theme)s::text is null or r.theme_primary = %(theme)s::text)
      and (
            %(sentiment)s::text is null
            or lower(trim(r.sentiment_label)) = %(sentiment)s::text
          )
      and r.review_date >= %(start_date)s::date
      and r.review_date <  (%(end_date)s::date + interval '1 day')
    group by 1, 2
    order by 1, 2;
    """
    params = {
        "bank_name": _as_optional_text(bank_name),
        "source": _as_optional_text(source),
        "theme": _as_optional_text(theme),
        # expected values: positive/negative/neutral
        "sentiment": _as_optional_text(sentiment),
        "start_date": start_date,
        "end_date": end_date,
    }
    return read_sql_df(sql, params=params, cfg=cfg)


def theme_breakdown(
    bank_name: str,
    source: str,
    start_date: str,
    end_date: str,
    cfg: Optional[DBConfig] = None,
) -> pd.DataFrame:
    """Theme x sentiment distribution for stacked bars / tables."""
    cfg = cfg or DBConfig.from_env()

    sql = """
    select
      b.bank_name,
      r.theme_primary,
      lower(trim(r.sentiment_label)) as sentiment_label,
      count(*) as n_reviews,
      avg(r.rating)::float as avg_rating,
      avg(r.sentiment_score)::float as avg_sentiment_score
    from reviews r
    join banks b on b.bank_id = r.bank_id
    where (%(bank_name)s::text is null or b.bank_name = %(bank_name)s::text)
      and (%(source)s::text is null or r.source = %(source)s::text)
      and r.review_date >= %(start_date)s::date
      and r.review_date <  (%(end_date)s::date + interval '1 day')
      and r.theme_primary is not null
      and r.sentiment_label is not null
    group by 1,2,3
    order by 1,2,3;
    """
    params = {
        "bank_name": _as_optional_text(bank_name),
        "source": _as_optional_text(source),
        "start_date": start_date,
        "end_date": end_date,
    }
    return read_sql_df(sql, params=params, cfg=cfg)


def sample_reviews(
    bank_name: str,
    theme: str,
    sentiment: str,
    start_date: str,
    end_date: str,
    limit: int = 15,
    cfg: Optional[DBConfig] = None,
) -> pd.DataFrame:
    """Evidence snippets table."""
    cfg = cfg or DBConfig.from_env()

    sql = """
    select
      r.review_date,
      b.bank_name,
      r.source,
      r.rating,
      lower(trim(r.sentiment_label)) as sentiment_label,
      r.sentiment_score,
      r.theme_primary,
      r.review_text
    from reviews r
    join banks b on b.bank_id = r.bank_id
    where (%(bank_name)s::text is null or b.bank_name = %(bank_name)s::text)
      and (%(theme)s::text is null or r.theme_primary = %(theme)s::text)
      and (
            %(sentiment)s::text is null
            or lower(trim(r.sentiment_label)) = %(sentiment)s::text
          )
      and r.review_date >= %(start_date)s::date
      and r.review_date <  (%(end_date)s::date + interval '1 day')
    order by r.review_date desc
    limit %(limit)s;
    """
    params = {
        "bank_name": _as_optional_text(bank_name),
        "theme": _as_optional_text(theme),
        "sentiment": _as_optional_text(sentiment),
        "start_date": start_date,
        "end_date": end_date,
        "limit": int(limit),
    }
    return read_sql_df(sql, params=params, cfg=cfg)
