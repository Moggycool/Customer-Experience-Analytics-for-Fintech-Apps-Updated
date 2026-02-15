""" Main entry point for the bank reviews project. 
    Orchestrates the entire data pipeline. """
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from bank_reviews.config import Paths, PipelineConfig, default_app_config
from bank_reviews.constants import (
    SCRAPE_TARGET_PER_BANK,
    MIN_REVIEWS_PER_BANK,
    NEUTRAL_MARGIN,
    BERT_BATCH_SIZE,
)

# These modules you will implement under the tree:
# from bank_reviews.scraping.play_store import scrape_all_banks
# from bank_reviews.preprocessing.clean_reviews import clean_reviews_rubric, clean_reviews_full
# from bank_reviews.nlp.sentiment import add_sentiment
# from bank_reviews.nlp.themes import add_themes
# from bank_reviews.db.load import load_to_postgres
# from bank_reviews.analysis.scenarios import build_scenario_tables
# from bank_reviews.viz.plots import save_all_figures
# from bank_reviews.modeling.train import train_tfidf_model
# from bank_reviews.modeling.explain import generate_shap_artifacts


def run(project_root: str | Path = ".") -> None:
    """Main function to run the entire bank reviews pipeline."""
    paths = Paths.from_root(project_root)
    app_cfg = default_app_config()
    pipe_cfg = PipelineConfig(
        scrape_target_per_bank=SCRAPE_TARGET_PER_BANK,
        min_reviews_per_bank=MIN_REVIEWS_PER_BANK,
        neutral_margin=NEUTRAL_MARGIN,
        bert_batch_size=BERT_BATCH_SIZE,
    )

    # Ensure directories exist
    for d in [
        paths.raw_dir, paths.interim_dir, paths.processed_dir, paths.figures_dir
    ]:
        d.mkdir(parents=True, exist_ok=True)

    print("Pipeline config:", asdict(pipe_cfg))

    # ---- Task 1: scrape + clean ----
    # raw_path = paths.raw_dir / "reviews_raw.csv"
    # scrape_all_banks(app_cfg=app_cfg, out_csv=raw_path, n_target=pipe_cfg.scrape_target_per_bank)

    # clean_rubric_path = paths.processed_dir / "reviews_clean.csv"
    # clean_full_path = paths.processed_dir / "reviews_clean_full.csv"
    # clean_reviews_rubric(raw_path, clean_rubric_path, app_cfg=app_cfg)
    # clean_reviews_full(raw_path, clean_full_path, app_cfg=app_cfg)

    # ---- Task 2: sentiment + themes ----
    # enriched_path = paths.processed_dir / "reviews_enriched.csv"
    # df = pd.read_csv(clean_full_path)
    # df = add_sentiment(df, neutral_margin=pipe_cfg.neutral_margin, batch_size=pipe_cfg.bert_batch_size)
    # df = add_themes(df)
    # df.to_csv(enriched_path, index=False)

    # ---- Task 3: load to Postgres ----
    # load_to_postgres(enriched_csv=enriched_path)

    # ---- Task 4: scenarios + plots ----
    # scenario_tables = build_scenario_tables(enriched_csv=enriched_path)
    # save_all_figures(enriched_csv=enriched_path, out_dir=paths.figures_dir)

    # ---- Extra (B): Model + SHAP + Dashboard assets ----
    # model_artifacts = train_tfidf_model(enriched_csv=enriched_path, out_dir=paths.interim_dir)
    # shap_outputs = generate_shap_artifacts(model_artifacts, out_dir=paths.reports_dir)

    print("Scaffold ready. Implement modules step-by-step per task branches.")


if __name__ == "__main__":
    run(".")
