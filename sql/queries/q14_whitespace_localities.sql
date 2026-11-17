-- Q14 | White-space localities: real demand signals, thin supply
-- Business question: where could a new outlet enter without landing in a saturated market?
WITH loc AS (
    SELECT l.locality_sk, l.locality_name, c.city_name,
           COUNT(*)                               AS listings,
           ROUND(AVG(f.cost_for_two), 0)          AS avg_cost,
           ROUND(AVG(f.rating), 2)                AS avg_rating,
           ROUND(AVG(f.rating_count), 0)          AS avg_reviews,
           ROUND(100.0 * SUM(CASE WHEN f.rating IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                  AS pct_rated
    FROM fact_listing f
    JOIN dim_locality l ON l.locality_sk = f.locality_sk
    JOIN dim_city     c ON c.city_sk     = l.city_sk
    GROUP BY l.locality_sk, l.locality_name, c.city_name
),
bench AS (
    SELECT AVG(listings) AS avg_listings, AVG(avg_cost) AS avg_cost,
           AVG(avg_rating) AS avg_rating
    FROM loc
)
SELECT
    l.city_name, l.locality_name, l.listings,
    ROUND(b.avg_listings - l.listings, 0)          AS listings_below_national_avg,
    l.avg_cost,
    ROUND(b.avg_cost - l.avg_cost, 0)              AS cost_vs_benchmark,
    l.avg_rating,
    l.avg_reviews,
    l.pct_rated
FROM loc l CROSS JOIN bench b
WHERE l.listings BETWEEN 8 AND 35
  AND l.avg_rating >= b.avg_rating
  AND l.pct_rated >= 30
ORDER BY l.avg_rating DESC, l.avg_reviews DESC
LIMIT 20;
