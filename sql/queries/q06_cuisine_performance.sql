-- Q06 | Cuisine supply vs satisfaction vs price (>=400 listings)
-- Business question: which cuisines have supply that outruns their ratings?
SELECT
    cu.cuisine_name                                                AS primary_cuisine,
    COUNT(*)                                                       AS listings,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM fact_listing), 2) AS pct_of_supply,
    ROUND(AVG(f.cost_for_two), 0)                                  AS avg_cost_for_two,
    ROUND(AVG(f.rating), 3)                                        AS avg_rating,
    ROUND(AVG(f.rating_count), 0)                                  AS avg_reviews,
    SUM(CASE WHEN f.rating IS NULL THEN 1 ELSE 0 END)              AS unrated_listings,
    ROUND(100.0 * SUM(CASE WHEN f.rating >= 4.0 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                                   AS pct_rated_4_plus
FROM fact_listing f
JOIN dim_cuisine cu ON cu.cuisine_sk = f.cuisine_sk
GROUP BY cu.cuisine_name
HAVING COUNT(*) >= 400
ORDER BY listings DESC;
