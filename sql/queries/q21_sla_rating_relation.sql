-- Q21 | Does delivery speed actually show up in ratings?
-- Business question: the operational metric the business can control, measured against satisfaction.
SELECT
    sla_band,
    COUNT(*)                                              AS listings,
    ROUND(AVG(delivery_min), 1)                           AS avg_delivery_min,
    ROUND(AVG(rating), 3)                                 AS avg_rating,
    ROUND(AVG(rating_count), 0)                           AS avg_reviews,
    ROUND(AVG(price_for_two), 0)                          AS avg_price_for_two,
    ROUND(100.0 * SUM(CASE WHEN rating >= 4.0 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                          AS pct_rated_4_plus
FROM fact_metro_sla
GROUP BY sla_band
ORDER BY avg_delivery_min;
