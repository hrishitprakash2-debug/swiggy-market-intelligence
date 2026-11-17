-- Q19 | Price-band share per city (where the mass market actually sits)
SELECT
    c.city_name,
    COUNT(*)                                                             AS listings,
    ROUND(100.0 * SUM(CASE WHEN pb.band_label = '<=150'   THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_upto_150,
    ROUND(100.0 * SUM(CASE WHEN pb.band_label = '151-250' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_151_250,
    ROUND(100.0 * SUM(CASE WHEN pb.band_label = '251-350' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_251_350,
    ROUND(100.0 * SUM(CASE WHEN pb.band_label = '351-500' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_351_500,
    ROUND(100.0 * SUM(CASE WHEN pb.band_order >= 5 THEN 1 ELSE 0 END) / COUNT(*), 1)        AS pct_501_plus
FROM fact_listing f
JOIN dim_locality   l  ON l.locality_sk   = f.locality_sk
JOIN dim_city       c  ON c.city_sk       = l.city_sk
JOIN dim_price_band pb ON pb.price_band_sk = f.price_band_sk
GROUP BY c.city_name
HAVING COUNT(*) >= 150
ORDER BY pct_501_plus DESC;
