"""
Gradio app for the bank reviews dashboard, including exploration
and model inference tabs.

This is a simple way to create an interactive dashboard without a full web framework.
It connects to the same database and models as the Flask app, but with a different UI layer.

Run:
    python -m src.bank_reviews.dashboard_gradio.app_gradio

Environment:
    - DATABASE_URL must be set (PostgreSQL connection string)
    - models/ must exist (sentiment.joblib, theme.joblib, meta.json)

Code organization:
    - data.py: database queries and caching
    - infer_bridge.py: bridge connecting Gradio to trained models
    - plots.py: plotting functions
    - impact.py: priority/impact table computation
    - components.py: reusable Gradio UI components (filters, controls)
    - app_gradio.py: app definition (this file)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence, cast

import os
import gradio as gr

from . import data, plots, impact
from .components import explore_controls
from .infer_bridge import load_predictor


def _bind_click(
    button: gr.Button,
    fn,
    *,
    inputs: Sequence[gr.Component] | gr.Component | None = None,
    outputs: Sequence[gr.Component] | gr.Component | None = None,
) -> None:
    """Bind a click handler while working around Gradio typing gaps."""
    cast(Any, button).click(fn=fn, inputs=inputs, outputs=outputs)


def _as_optional_filter(v: Any) -> Any:
    """
    Normalize UI filter values to what SQL expects.

    Important: Your SQL uses patterns like:
        WHERE ($1 IS NULL OR b.bank_name = $1)

    In PostgreSQL, the driver must be able to infer $1 type.
    Passing a bare NULL can trigger:
        could not determine data type of parameter $1

    So: prefer passing a real string when possible, otherwise None,
    but only if your query is written in a way that safely types the param
    (e.g., using CAST in SQL). Since your current query seems to error,
    we avoid passing None when the user selected "All" by translating "All"
    to empty-string sentinel *or* keeping "All" out of the SQL entirely.

    Because we don't control data.py SQL here, the safest immediate fix is:
      - return None for "All"/"" but ALSO encourage fixing SQL with explicit casts.
    """
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        if s == "" or s.lower() == "all":
            return None
        return s
    return v


def _diagnostics() -> dict[str, Any]:
    """Lightweight startup diagnostics for env + model artifacts."""
    cwd = Path.cwd()
    model_dir = cwd / "models"
    return {
        "cwd": str(cwd),
        "database_url_set": bool(os.environ.get("DATABASE_URL")),
        "models_dir_exists": model_dir.exists(),
        "sentiment_model_exists": (model_dir / "sentiment.joblib").exists(),
        "theme_model_exists": (model_dir / "theme.joblib").exists(),
        "meta_exists": (model_dir / "meta.json").exists(),
    }


def build_app() -> gr.Blocks:
    """Build the Gradio Blocks app with Explore/Predict/Impact tabs."""
    filters = data.get_filters()
    predictor = load_predictor()

    with gr.Blocks(title="Bank CX Dashboard (Gradio)") as demo:
        gr.Markdown("# Bank Customer Experience Dashboard")
        gr.Markdown(
            "Set `DATABASE_URL` before running. Models are loaded from `./models` by default.")

        with gr.Accordion("Startup diagnostics (click to expand)", open=False):
            gr.JSON(value=_diagnostics(), label="Environment check")

        # --------------------
        # Explore
        # --------------------
        with gr.Tab("Explore"):
            with gr.Row():
                bank, source, theme, sentiment, metric, start, end = explore_controls(
                    filters)

            run = gr.Button("Run")

            fig_trend = gr.Plot(label="Trend")
            tbl_monthly = gr.Dataframe(
                label="Monthly summary", interactive=False)

            fig_theme = gr.Plot(label="Theme x Sentiment")
            tbl_theme = gr.Dataframe(
                label="Theme breakdown", interactive=False)

            tbl_samples = gr.Dataframe(
                label="Evidence samples", interactive=False)

            def _run(bank, source, theme, sentiment, metric, start, end):
                """
                Run exploration queries and update charts/tables.

                Key fix:
                - Convert "All"/"" to None before passing to data layer.
                This avoids passing UI sentinel values into SQL filters.
                """
                bank_f = _as_optional_filter(bank)
                source_f = _as_optional_filter(source)
                theme_f = _as_optional_filter(theme)
                sentiment_f = _as_optional_filter(sentiment)

                df_month = data.monthly_summary(
                    bank_f, source_f, theme_f, sentiment_f, start, end)
                trend = plots.line_metric_over_time(df_month, metric)

                df_theme = data.theme_breakdown(bank_f, source_f, start, end)
                stacked = plots.stacked_theme_sentiment(df_theme)

                # default to negative samples if sentiment not specified
                sample_sent = (sentiment_f or "negative")
                if isinstance(sample_sent, str):

                    sample_sent = sample_sent.strip()
                    sample_sent = sample_sent if sample_sent != "All" else "negative"
                df_samples = data.sample_reviews(
                    bank_f, theme_f, sample_sent, start, end, limit=15
                )

                return trend, df_month, stacked, df_theme, df_samples

            _bind_click(
                run,
                _run,
                inputs=[bank, source, theme, sentiment, metric, start, end],
                outputs=[fig_trend, tbl_monthly,
                         fig_theme, tbl_theme, tbl_samples],
            )

        # --------------------
        # Predict
        # --------------------
        with gr.Tab("Predict"):
            txt = gr.Textbox(lines=6, label="Paste a review")
            out = gr.JSON(label="Prediction (sentiment + theme)")

            def _predict(text: str):
                pred = predictor(text)
                if hasattr(pred, "as_dict"):
                    return pred.as_dict()
                if isinstance(pred, dict):
                    return pred
                return {"result": str(pred)}

            predict_btn = gr.Button("Predict")
            _bind_click(predict_btn, _predict, inputs=txt, outputs=out)

        # --------------------
        # Impact
        # --------------------
        with gr.Tab("Impact"):
            gr.Markdown("## Drivers vs Pain Points (priority table)")

            with gr.Row():
                bank_i = gr.Dropdown(
                    choices=filters["banks"], value="All", label="Bank")
                source_i = gr.Dropdown(
                    choices=filters["sources"], value="All", label="Source")
                start_i = gr.Textbox(value="2024-01-01",
                                     label="Start date (YYYY-MM-DD)")
                end_i = gr.Textbox(value="2026-12-31",
                                   label="End date (YYYY-MM-DD)")
                btn = gr.Button("Compute")

            pri_tbl = gr.Dataframe(interactive=False)

            def _compute(bank_name, source, start_date, end_date):
                """Compute the priority table for themes based on sentiment and volume."""
                bank_f = _as_optional_filter(bank_name)
                source_f = _as_optional_filter(source)
                theme_df = data.theme_breakdown(
                    bank_f, source_f, start_date, end_date)
                return impact.compute_priority_table(theme_df)

            _bind_click(
                btn,
                _compute,
                inputs=[bank_i, source_i, start_i, end_i],
                outputs=pri_tbl,
            )

    return demo


def main() -> None:
    """Main entry point to launch the Gradio app."""
    app = build_app()
    # Debug + show_error ensures you see full tracebacks in terminal/browser
    app.launch(debug=True, show_error=True)


if __name__ == "__main__":
    main()
