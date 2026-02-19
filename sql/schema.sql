-- sql/schema.sql
BEGIN;

CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name TEXT NOT NULL UNIQUE,
    app_name TEXT
);


CREATE TABLE IF NOT EXISTS reviews (
    review_id        BIGSERIAL PRIMARY KEY,  -- generated at load time (Task 1)
    bank_id          INTEGER NOT NULL REFERENCES banks(bank_id) ON DELETE CASCADE,

    review_text      TEXT NOT NULL,
    rating           INTEGER CHECK (rating BETWEEN 1 AND 5),
    review_date      DATE,
    source           TEXT,

-- deterministic key for matching Task2 <-> Task1
review_hash TEXT NOT NULL UNIQUE,

-- enrichment columns (filled later from Task 2)
sentiment_label  TEXT CHECK (sentiment_label IN ('POSITIVE','NEGATIVE','NEUTRAL')),
    sentiment_score  DOUBLE PRECISION,
    theme_primary    TEXT
);

CREATE TABLE IF NOT EXISTS themes (
    theme_id SERIAL PRIMARY KEY,
    theme_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS review_themes (
    review_id BIGINT NOT NULL REFERENCES reviews (review_id) ON DELETE CASCADE,
    theme_id INTEGER NOT NULL REFERENCES themes (theme_id) ON DELETE CASCADE,
    PRIMARY KEY (review_id, theme_id)
);

CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews (bank_id);

CREATE INDEX IF NOT EXISTS idx_reviews_review_date ON reviews (review_date);

CREATE INDEX IF NOT EXISTS idx_reviews_source ON reviews (source);

CREATE INDEX IF NOT EXISTS idx_reviews_theme_primary ON reviews (theme_primary);

COMMIT;