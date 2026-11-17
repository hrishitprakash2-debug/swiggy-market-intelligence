-- Q02 | City supply share + cumulative Pareto (window functions)
-- Business question: which cities dominate supply, and how few hold most of it?
WITH city_listings AS (
    SELECT c.city_name, COUNT(*) AS listings
    FROM fact_listing f
    JOIN dim_locality l ON l.locality_sk = f.locality_sk
    JOIN dim_city    c ON c.city_sk     = l.city_sk
    GROUP BY c.city_name
)
SELECT
    RANK() OVER (ORDER BY listings DESC)                          AS rank_by_supply,
    city_name,
    listings,
    ROUND(100.0 * listings / SUM(listings) OVER (), 2)            AS pct_of_national_supply,
    ROUND(100.0 * SUM(listings) OVER (ORDER BY listings DESC
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
          / SUM(listings) OVER (), 2)                             AS cumulative_pct
FROM city_listings
ORDER BY listings DESC
LIMIT 20;
