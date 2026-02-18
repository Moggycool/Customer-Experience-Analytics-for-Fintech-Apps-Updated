"""This module contains the logging configuration for the bank reviews analysis project.
"""
# src/bank_reviews/logging_config.py
from __future__ import annotations
import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
