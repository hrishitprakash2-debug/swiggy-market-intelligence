-- Q08 | Does review volume change the rating story?
-- Business question: are high ratings earned, or an artefact of thin review volume?
SELECT
    dc.confidence_label,
    dc.confidence_order,
    COUNT(*)                                                       AS listings,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM fact_listing), 1) AS pct_of_supply,
    ROUND(AVG(f.rating), 3)                                        AS avg_rating,
    ROUND(AVG(f.rating_count), 0)                                  AS avg_reviews,
    ROUND(AVG(f.cost_for_two), 0)                                  AS avg_cost_for_two,
    ROUND(100.0 * SUM(CASE WHEN f.rating >= 4.2 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                                   AS pct_at_or_above_4_2
FROM fact_listing f
JOIN dim_review_confidence dc ON dc.confidence_sk = f.confidence_sk
GROUP BY dc.confidence_label, dc.confidence_order
ORDER BY dc.confidence_order;
