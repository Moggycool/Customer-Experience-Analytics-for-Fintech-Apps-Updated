"""Gradio components for the bank reviews dashboard."""
from __future__ import annotations
import gradio as gr


def explore_controls(filters: dict[str, list[str]]):
    """Create the filter controls for the Explore tab."""
    bank = gr.Dropdown(choices=filters["banks"], value="All", label="Bank")
    source = gr.Dropdown(
        choices=filters["sources"], value="All", label="Source")
    theme = gr.Dropdown(choices=filters["themes"], value="All", label="Theme")
    sentiment = gr.Dropdown(
        choices=filters["sentiments"], value="All", label="Sentiment")

    metric = gr.Dropdown(
        choices=["Negative share", "Positive share",
                 "Avg rating", "Review volume", "Avg sentiment score"],
        value="Negative share",
        label="Metric",
    )
    start = gr.Textbox(value="2024-01-01", label="Start date (YYYY-MM-DD)")
    end = gr.Textbox(value="2026-12-31", label="End date (YYYY-MM-DD)")

    return bank, source, theme, sentiment, metric, start, end
