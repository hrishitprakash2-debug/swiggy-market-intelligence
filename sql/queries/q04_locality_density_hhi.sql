-- Q04 | Densest localities with cuisine concentration (HHI, 0-10,000)
-- Business question: where is competition brutal, and is it fragmented or dominated?
WITH loc_total AS (
    SELECT locality_sk, COUNT(*) AS n FROM fact_listing GROUP BY locality_sk
),
cu AS (
    SELECT locality_sk, cuisine_sk, COUNT(*) AS k
    FROM fact_listing GROUP BY locality_sk, cuisine_sk
),
hhi AS (
    SELECT cu.locality_sk, ROUND(SUM((1.0 * cu.k / lt.n) * (1.0 * cu.k / lt.n)) * 10000, 0) AS hhi
    FROM cu JOIN loc_total lt ON lt.locality_sk = cu.locality_sk
    GROUP BY cu.locality_sk
)
SELECT
    l.locality_name,
    c.city_name,
    lt.n                                                          AS listings,
    h.hhi                                                         AS cuisine_hhi,
    ROUND(AVG(f.cost_for_two), 0)                                 AS avg_cost_for_two,
    ROUND(AVG(f.rating), 2)                                       AS avg_rating,
    COUNT(DISTINCT f.cuisine_sk)                                  AS distinct_cuisines,
    ROUND(100.0 * SUM(CASE WHEN f.rating IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                                  AS pct_unrated
FROM fact_listing f
JOIN dim_locality l ON l.locality_sk = f.locality_sk
JOIN dim_city     c ON c.city_sk     = l.city_sk
JOIN loc_total   lt ON lt.locality_sk = f.locality_sk
JOIN hhi          h ON h.locality_sk  = f.locality_sk
GROUP BY l.locality_name, c.city_name, lt.n, h.hhi
ORDER BY listings DESC
LIMIT 25;
