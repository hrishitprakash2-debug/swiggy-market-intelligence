-- Q09 | Unrated share by city — the visibility gap
-- Business question: in which cities is most supply invisible to rank-based discovery?
WITH g AS (
    SELECT c.city_name,
           COUNT(*) AS listings,
           SUM(CASE WHEN f.rating IS NULL THEN 1 ELSE 0 END) AS unrated,
           ROUND(AVG(f.rating), 2) AS avg_rating_when_rated,
           ROUND(AVG(f.cost_for_two), 0) AS avg_cost
    FROM fact_listing f
    JOIN dim_locality l ON l.locality_sk = f.locality_sk
    JOIN dim_city     c ON c.city_sk     = l.city_sk
    GROUP BY c.city_name
)
SELECT
    city_name, listings, unrated,
    ROUND(100.0 * unrated / listings, 1) AS pct_unrated,
    avg_rating_when_rated, avg_cost,
    ROUND(100.0 * unrated / listings - AVG(100.0 * unrated / listings) OVER (), 1)
                                         AS pct_unrated_vs_national
FROM g
WHERE listings >= 150
ORDER BY pct_unrated DESC
LIMIT 20;
