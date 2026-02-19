from __future__ import annotations

import os
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@dataclass(frozen=True)
class DBConfig:
    database_url: str


def get_db_config() -> DBConfig:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set.\n"
            "Example: postgresql+psycopg2://postgres:PASSWORD@localhost:5432/bank_reviews"
        )
    return DBConfig(database_url=url)


def get_engine(*, echo: bool = False) -> Engine:
    cfg = get_db_config()
    return create_engine(cfg.database_url, echo=echo, future=True, pool_pre_ping=True)
