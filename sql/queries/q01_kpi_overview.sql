-- Q01 | Headline KPIs for the whole marketplace
-- Business question: what does the supply base actually look like?
SELECT
    COUNT(*)                                                    AS total_listings,
    COUNT(DISTINCT l.city_sk)                                   AS cities,
    COUNT(DISTINCT f.locality_sk)                               AS localities,
    COUNT(DISTINCT f.cuisine_sk)                                AS primary_cuisines,
    ROUND(AVG(f.cost_for_two), 1)                               AS avg_cost_for_two_inr,
    ROUND(AVG(f.rating), 3)                                     AS avg_rating_when_rated,
    ROUND(AVG(f.rating_count), 0)                               AS avg_reviews_when_rated,
    ROUND(100.0 * SUM(CASE WHEN f.rating IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                                AS pct_listings_unrated,
    ROUND(100.0 * SUM(CASE WHEN f.cuisine_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                                AS pct_multi_cuisine
FROM fact_listing f
JOIN dim_locality l ON l.locality_sk = f.locality_sk;
