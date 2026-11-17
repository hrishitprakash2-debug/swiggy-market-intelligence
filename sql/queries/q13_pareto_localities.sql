-- Q13 | How concentrated is supply across localities? (Pareto by window sum)
-- Business question: how many localities carry 50% / 80% of all listings?
WITH loc AS (
    SELECT l.locality_name, c.city_name, COUNT(*) AS listings
    FROM fact_listing f
    JOIN dim_locality l ON l.locality_sk = f.locality_sk
    JOIN dim_city     c ON c.city_sk     = l.city_sk
    GROUP BY l.locality_name, c.city_name
),
cum AS (
    SELECT *,
           ROW_NUMBER() OVER (ORDER BY listings DESC) AS rn,
           SUM(listings) OVER (ORDER BY listings DESC
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running,
           SUM(listings) OVER ()                                AS total
    FROM loc
)
SELECT locality_name, city_name, listings, rn AS locality_rank,
       ROUND(100.0 * running / total, 1) AS cumulative_pct_of_supply
FROM cum
WHERE rn <= 30
ORDER BY rn;
