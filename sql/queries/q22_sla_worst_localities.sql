-- Q22 | Operational worst-case localities (min 25 outlets, metro data)
-- Business question: where is the delivery experience structurally slow?
SELECT
    dc.city_name,
    l.locality_name,
    COUNT(*)                                                    AS listings,
    ROUND(AVG(s.delivery_min), 1)                               AS avg_delivery_min,
    ROUND(AVG(s.rating), 2)                                     AS avg_rating,
    ROUND(100.0 * SUM(CASE WHEN s.delivery_min > 60 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                                AS pct_over_60min
FROM fact_metro_sla s
JOIN dim_locality l  ON l.locality_sk = s.locality_sk
JOIN dim_city     dc ON dc.city_sk    = l.city_sk
GROUP BY dc.city_name, l.locality_name
HAVING COUNT(*) >= 25
ORDER BY avg_delivery_min DESC
LIMIT 15;
