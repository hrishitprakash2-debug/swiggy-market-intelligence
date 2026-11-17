-- Q03 | City price index vs national median (median via window ROW_NUMBER)
-- Business question: which cities are expensive relative to the country, not just in rupees?
WITH ranked AS (
    SELECT c.city_name, f.cost_for_two,
           ROW_NUMBER()   OVER (PARTITION BY c.city_name ORDER BY f.cost_for_two) AS rn,
           COUNT(*)       OVER (PARTITION BY c.city_name)                        AS cnt
    FROM fact_listing f
    JOIN dim_locality l ON l.locality_sk = f.locality_sk
    JOIN dim_city    c ON c.city_sk     = l.city_sk
    WHERE f.cost_for_two IS NOT NULL
),
city_median AS (
    SELECT city_name, AVG(cost_for_two) AS median_cost, MAX(cnt) AS n_listings
    FROM ranked
    WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
    GROUP BY city_name
),
national AS (
    SELECT AVG(cost_for_two) AS national_median
    FROM (SELECT cost_for_two,
                 ROW_NUMBER() OVER (ORDER BY cost_for_two) AS rn,
                 COUNT(*)     OVER ()                     AS cnt
          FROM fact_listing WHERE cost_for_two IS NOT NULL)
    WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2)
)
SELECT
    cm.city_name,
    cm.n_listings,
    ROUND(cm.median_cost, 0)                                      AS median_cost_for_two_inr,
    ROUND(cm.median_cost / n.national_median, 3)                  AS price_index_national_1x,
    ROUND(cm.median_cost - n.national_median, 0)                  AS inr_above_national_median
FROM city_median cm
CROSS JOIN national n
WHERE cm.n_listings >= 150
ORDER BY price_index_national_1x DESC;
