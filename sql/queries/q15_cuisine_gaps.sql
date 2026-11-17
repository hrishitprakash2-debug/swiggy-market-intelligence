-- Q15 | Cuisine under-penetration: cities where a proven cuisine is under-represented
-- Business question: not "where is it absent" (the big cuisines are everywhere) but
-- "where is it far below its national share, while local demand quality is high?"
WITH nat AS (
    SELECT b.cuisine_sk, cu.cuisine_name,
           1.0 * COUNT(*) / (SELECT COUNT(*) FROM fact_listing) AS national_share
    FROM bridge_listing_cuisine b
    JOIN dim_cuisine cu ON cu.cuisine_sk = b.cuisine_sk
    GROUP BY b.cuisine_sk, cu.cuisine_name
    ORDER BY COUNT(*) DESC
    LIMIT 10
),
city_tot AS (
    SELECT l.city_sk, COUNT(*) AS listings, AVG(f.rating) AS avg_rating
    FROM fact_listing f JOIN dim_locality l ON l.locality_sk = f.locality_sk
    GROUP BY l.city_sk HAVING COUNT(*) >= 300
),
city_cu AS (
    SELECT l.city_sk, b.cuisine_sk, COUNT(*) AS outlets
    FROM fact_listing f
    JOIN dim_locality l ON l.locality_sk = f.locality_sk
    JOIN bridge_listing_cuisine b ON b.listing_id = f.listing_id
    GROUP BY l.city_sk, b.cuisine_sk
)
SELECT
    dc.city_name,
    ct.listings                                                   AS city_listings,
    ROUND(ct.avg_rating, 2)                                       AS city_avg_rating,
    nat.cuisine_name,
    ROUND(100.0 * nat.national_share, 1)                          AS national_penetration_pct,
    COALESCE(cc.outlets, 0)                                       AS city_outlets,
    ROUND(100.0 * COALESCE(cc.outlets, 0) / ct.listings, 1)       AS city_penetration_pct,
    ROUND(100.0 * COALESCE(cc.outlets, 0) / ct.listings
          - 100.0 * nat.national_share, 1)                         AS penetration_gap_pp
FROM city_tot ct
JOIN dim_city dc ON dc.city_sk = ct.city_sk
CROSS JOIN nat
LEFT JOIN city_cu cc ON cc.city_sk = ct.city_sk AND cc.cuisine_sk = nat.cuisine_sk
WHERE ct.avg_rating >= (SELECT AVG(rating) FROM fact_listing WHERE rating IS NOT NULL)
  AND (100.0 * COALESCE(cc.outlets, 0) / ct.listings) < 60.0 * (100.0 * nat.national_share)
ORDER BY penetration_gap_pp
LIMIT 30;
