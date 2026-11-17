-- Q07 | Cuisine x price-band matrix (conditional aggregation pivot)
-- Business question: at what price point does each cuisine actually compete?
SELECT
    cu.cuisine_name,
    COUNT(*)                                                              AS listings,
    SUM(CASE WHEN pb.band_label = '<=150'    THEN 1 ELSE 0 END)            AS b_upto_150,
    SUM(CASE WHEN pb.band_label = '151-250'  THEN 1 ELSE 0 END)            AS b_151_250,
    SUM(CASE WHEN pb.band_label = '251-350'  THEN 1 ELSE 0 END)            AS b_251_350,
    SUM(CASE WHEN pb.band_label = '351-500'  THEN 1 ELSE 0 END)            AS b_351_500,
    SUM(CASE WHEN pb.band_label = '501-750'  THEN 1 ELSE 0 END)            AS b_501_750,
    SUM(CASE WHEN pb.band_label = '750+'     THEN 1 ELSE 0 END)            AS b_750_plus,
    ROUND(100.0 * SUM(CASE WHEN pb.band_order >= 5 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                                          AS pct_premium_501_plus
FROM fact_listing f
JOIN dim_cuisine    cu ON cu.cuisine_sk    = f.cuisine_sk
JOIN dim_price_band pb ON pb.price_band_sk = f.price_band_sk
GROUP BY cu.cuisine_name
HAVING COUNT(*) >= 400
ORDER BY pct_premium_501_plus DESC;
