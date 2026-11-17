-- Q10 | Rating-band distribution per city (quality spread, not just averages)
-- Business question: is a city's average rating hiding a bimodal quality split?
SELECT
    c.city_name,
    COUNT(*)                                                       AS listings,
    SUM(CASE WHEN f.rating_band = '<=3.0'   THEN 1 ELSE 0 END)      AS rb_upto_3_0,
    SUM(CASE WHEN f.rating_band = '3.1-3.5' THEN 1 ELSE 0 END)      AS rb_3_1_3_5,
    SUM(CASE WHEN f.rating_band = '3.6-4.0' THEN 1 ELSE 0 END)      AS rb_3_6_4_0,
    SUM(CASE WHEN f.rating_band = '4.1-4.5' THEN 1 ELSE 0 END)      AS rb_4_1_4_5,
    SUM(CASE WHEN f.rating_band = '4.6-5.0' THEN 1 ELSE 0 END)      AS rb_4_6_5_0,
    SUM(CASE WHEN f.rating IS NULL         THEN 1 ELSE 0 END)       AS unrated,
    ROUND(100.0 * SUM(CASE WHEN f.rating_band = '<=3.0' THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN f.rating IS NOT NULL THEN 1 ELSE 0 END), 0), 1)
                                                                   AS pct_of_rated_below_3
FROM fact_listing f
JOIN dim_locality l ON l.locality_sk = f.locality_sk
JOIN dim_city     c ON c.city_sk     = l.city_sk
GROUP BY c.city_name
HAVING COUNT(*) >= 150
ORDER BY listings DESC
LIMIT 20;
