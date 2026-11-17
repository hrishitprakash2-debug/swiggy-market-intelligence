-- Q12 | Price deciles vs achieved rating (NTILE)
-- Business question: does charging more buy a better rating, or does it cap it?
WITH d AS (
    SELECT f.cost_for_two, f.rating, f.rating_count,
           NTILE(10) OVER (ORDER BY f.cost_for_two) AS price_decile
    FROM fact_listing f
    WHERE f.cost_for_two IS NOT NULL
)
SELECT
    price_decile,
    COUNT(*)                                                   AS listings,
    ROUND(MIN(cost_for_two), 0)                                AS decile_min_cost,
    ROUND(MAX(cost_for_two), 0)                                AS decile_max_cost,
    ROUND(AVG(rating), 3)                                      AS avg_rating,
    ROUND(AVG(rating_count), 0)                                AS avg_reviews,
    ROUND(100.0 * SUM(CASE WHEN rating IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_unrated
FROM d
GROUP BY price_decile
ORDER BY price_decile;
