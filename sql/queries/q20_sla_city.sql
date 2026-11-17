-- Q20 | Service level by metro: median delivery time and SLA breach rate
-- Business question: which metros systematically miss a 45-minute promise?
WITH r AS (
    SELECT s.locality_sk, dc.city_name, s.delivery_min, s.rating, s.price_for_two,
           ROW_NUMBER() OVER (PARTITION BY dc.city_name ORDER BY s.delivery_min) AS rn,
           COUNT(*)     OVER (PARTITION BY dc.city_name)                         AS cnt
    FROM fact_metro_sla s
    JOIN dim_locality l ON l.locality_sk = s.locality_sk
    JOIN dim_city    dc ON dc.city_sk    = l.city_sk
),
base AS (
    SELECT l.city_sk,
           COUNT(*)                                                     AS listings,
           AVG(s.delivery_min)                                          AS avg_delivery,
           AVG(s.rating)                                                AS avg_rating,
           AVG(s.price_for_two)                                         AS avg_price,
           SUM(CASE WHEN s.delivery_min > 45 THEN 1 ELSE 0 END)         AS breach_45,
           SUM(CASE WHEN s.delivery_min > 60 THEN 1 ELSE 0 END)         AS breach_60
    FROM fact_metro_sla s
    JOIN dim_locality l ON l.locality_sk = s.locality_sk
    GROUP BY l.city_sk
),
med AS (
    SELECT locality_sk, city_name, AVG(delivery_min) AS median_delivery
    FROM r WHERE rn IN ((cnt + 1) / 2, (cnt + 2) / 2) GROUP BY city_name
)
SELECT
    m.city_name,
    b.listings,
    ROUND(b.avg_delivery, 1)                                   AS avg_delivery_min,
    ROUND(m.median_delivery, 1)                                AS median_delivery_min,
    ROUND(100.0 * b.breach_45 / b.listings, 1)                 AS pct_breach_45min,
    ROUND(100.0 * b.breach_60 / b.listings, 1)                 AS pct_breach_60min,
    ROUND(b.avg_rating, 2)                                     AS avg_rating,
    ROUND(b.avg_price, 0)                                      AS avg_price_for_two
FROM base b
JOIN dim_city dc ON dc.city_sk = b.city_sk
JOIN med      m  ON m.city_name = dc.city_name
ORDER BY pct_breach_45min DESC;
