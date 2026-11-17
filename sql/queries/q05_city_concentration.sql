-- Q05 | City-level market concentration across cuisines
-- Business question: do big cities fragment into many cuisines or concentrate?
WITH city_total AS (
    SELECT l.city_sk, COUNT(*) AS n
    FROM fact_listing f JOIN dim_locality l ON l.locality_sk = f.locality_sk
    GROUP BY l.city_sk
),
cu AS (
    SELECT l.city_sk, f.cuisine_sk, COUNT(*) AS k
    FROM fact_listing f JOIN dim_locality l ON l.locality_sk = f.locality_sk
    GROUP BY l.city_sk, f.cuisine_sk
),
hhi AS (
    SELECT cu.city_sk, SUM((1.0 * cu.k / ct.n) * (1.0 * cu.k / ct.n)) * 10000 AS hhi,
           MAX(1.0 * cu.k / ct.n) * 100 AS top_cuisine_share_pct
    FROM cu JOIN city_total ct ON ct.city_sk = cu.city_sk
    GROUP BY cu.city_sk
)
SELECT
    c.city_name,
    ct.n                                             AS listings,
    COUNT(DISTINCT f.cuisine_sk)                     AS cuisines_present,
    ROUND(h.hhi, 0)                                  AS cuisine_hhi,
    ROUND(h.top_cuisine_share_pct, 1)                AS largest_cuisine_share_pct,
    CASE WHEN h.hhi < 1500 THEN 'Fragmented'
         WHEN h.hhi < 2500 THEN 'Moderately concentrated'
         ELSE 'Concentrated' END                     AS structure
FROM fact_listing f
JOIN dim_locality l ON l.locality_sk = f.locality_sk
JOIN dim_city     c ON c.city_sk     = l.city_sk
JOIN city_total  ct ON ct.city_sk    = l.city_sk
JOIN hhi          h ON h.city_sk     = l.city_sk
WHERE ct.n >= 200
GROUP BY c.city_name, ct.n, h.hhi, h.top_cuisine_share_pct
ORDER BY listings DESC
LIMIT 25;
