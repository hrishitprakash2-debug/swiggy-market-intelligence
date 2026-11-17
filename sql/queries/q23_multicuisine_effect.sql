-- Q23 | Cuisine co-occurrence: which cuisines get bundled on the same menu, and does it help?
-- Note: Swiggy tags at most two cuisines per outlet, so "menu breadth" is degenerate;
-- the useful question is which *pairings* exist and how they rate.
WITH pairs AS (
    SELECT a.listing_id, a.cuisine_sk AS s1, b.cuisine_sk AS s2
    FROM bridge_listing_cuisine a
    JOIN bridge_listing_cuisine b
      ON b.listing_id = a.listing_id AND a.cuisine_sk < b.cuisine_sk
)
SELECT
    c1.cuisine_name                                               AS cuisine_a,
    c2.cuisine_name                                               AS cuisine_b,
    COUNT(*)                                                      AS outlets,
    ROUND(AVG(f.rating), 3)                                       AS avg_rating,
    ROUND(AVG(f.cost_for_two), 0)                                 AS avg_cost_for_two,
    ROUND(100.0 * SUM(CASE WHEN f.rating >= 4.0 THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                                  AS pct_rated_4_plus,
    ROUND(AVG(f.rating) - (SELECT AVG(rating) FROM fact_listing WHERE rating IS NOT NULL), 3)
                                                                  AS rating_vs_national
FROM pairs p
JOIN fact_listing f ON f.listing_id = p.listing_id
JOIN dim_cuisine c1 ON c1.cuisine_sk = p.s1
JOIN dim_cuisine c2 ON c2.cuisine_sk = p.s2
GROUP BY c1.cuisine_name, c2.cuisine_name
HAVING COUNT(*) >= 150
ORDER BY outlets DESC
LIMIT 25;
