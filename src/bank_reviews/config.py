""" Configuration classes and factory functions for the bank reviews project. """
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass(frozen=True)
class AppConfig:
    """Google Play app identifiers and bank display names."""
    app_ids: Dict[str, str]
    bank_names: Dict[str, str]
    source_name: str = "Google Play"
    lang: str = "en"
    country: str = "et"


@dataclass(frozen=True)
class Paths:
    """All filesystem paths used by the project."""
    project_root: Path
    data_dir: Path
    raw_dir: Path
    interim_dir: Path
    processed_dir: Path
    reports_dir: Path
    figures_dir: Path

    @staticmethod
    def from_root(project_root: str | Path) -> "Paths":
        """Factory method to create Paths from a given project root directory."""
        root = Path(project_root).resolve()
        data_dir = root / "data"
        reports_dir = root / "reports"
        return Paths(
            project_root=root,
            data_dir=data_dir,
            raw_dir=data_dir / "raw",
            interim_dir=data_dir / "interim",
            processed_dir=data_dir / "processed",
            reports_dir=reports_dir,
            figures_dir=reports_dir / "figures",
        )


@dataclass(frozen=True)
class DBConfig:
    """Local PostgreSQL connection settings (no secrets committed)."""
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = ""     # set via env in real usage
    database: str = "bank_reviews"


@dataclass(frozen=True)
class PipelineConfig:
    """End-to-end pipeline knobs."""
    scrape_target_per_bank: int
    min_reviews_per_bank: int
    neutral_margin: float
    bert_batch_size: int


def default_app_config() -> AppConfig:
    """Factory function for the default app configuration."""
    return AppConfig(
        app_ids={
            "CBE": "com.combanketh.mobilebanking",
            "BOA": "com.boa.boaMobileBanking",
            "DASHEN": "com.dashen.dashensuperapp",
        },
        bank_names={
            "CBE": "Commercial Bank of Ethiopia",
            "BOA": "Bank of Abyssinia",
            "DASHEN": "Dashen Bank",
        },
    )
