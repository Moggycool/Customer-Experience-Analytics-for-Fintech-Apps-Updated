-- sql/verify.sql

-- Total rows
SELECT COUNT(*) AS total_reviews FROM reviews;

-- Reviews per bank
SELECT b.bank_name, COUNT(*) AS n_reviews
FROM reviews r
    JOIN banks b ON b.bank_id = r.bank_id
GROUP BY
    b.bank_name
ORDER BY n_reviews DESC;

-- Avg rating per bank
SELECT b.bank_name, ROUND(AVG(r.rating)::numeric, 2) AS avg_rating
FROM reviews r
    JOIN banks b ON b.bank_id = r.bank_id
GROUP BY
    b.bank_name
ORDER BY avg_rating DESC;

-- Enrichment coverage
SELECT
    COUNT(*) AS total,
    SUM(
        CASE
            WHEN sentiment_label IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS with_sentiment_label,
    SUM(
        CASE
            WHEN sentiment_score IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS with_sentiment_score,
    SUM(
        CASE
            WHEN theme_primary IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS with_theme_primary
FROM reviews;

-- Any Task2 rows not found in reviews? (should be 0 if IDs match)
-- Run this after you load Task2_scored into a temp table OR use Python check.