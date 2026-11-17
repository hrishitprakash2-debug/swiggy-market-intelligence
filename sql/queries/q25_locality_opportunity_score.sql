-- Q25 | Composite locality opportunity score (percentile scoring, no ML)
-- Business question: rank localities on demand quality instead of raw outlet count.
-- Score = 35% rating + 25% review depth + 20% price headroom + 20% low saturation.
WITH loc AS (
    SELECT l.locality_sk, l.locality_name, c.city_name,
           COUNT(*)                        AS listings,
           AVG(f.rating)                   AS avg_rating,
           AVG(f.rating_count)             AS avg_reviews,
           AVG(f.cost_for_two)             AS avg_cost
    FROM fact_listing f
    JOIN dim_locality l ON l.locality_sk = f.locality_sk
    JOIN dim_city     c ON c.city_sk     = l.city_sk
    GROUP BY l.locality_sk, l.locality_name, c.city_name
    HAVING COUNT(*) >= 20
),
scored AS (
    SELECT *,
        PERCENT_RANK() OVER (ORDER BY avg_rating)   AS p_rating,
        PERCENT_RANK() OVER (ORDER BY avg_reviews)  AS p_reviews,
        PERCENT_RANK() OVER (ORDER BY avg_cost)     AS p_price,
        PERCENT_RANK() OVER (ORDER BY -listings)    AS p_low_saturation
    FROM loc
)
SELECT
    RANK() OVER (ORDER BY 0.35 * p_rating + 0.25 * p_reviews
                          + 0.20 * p_price + 0.20 * p_low_saturation DESC) AS opportunity_rank,
    city_name, locality_name, listings,
    ROUND(avg_rating, 2)  AS avg_rating,
    ROUND(avg_reviews, 0) AS avg_reviews,
    ROUND(avg_cost, 0)    AS avg_cost_for_two,
    ROUND(100.0 * (0.35 * p_rating + 0.25 * p_reviews
                   + 0.20 * p_price + 0.20 * p_low_saturation), 1) AS opportunity_score
FROM scored
ORDER BY opportunity_score DESC
LIMIT 20;
