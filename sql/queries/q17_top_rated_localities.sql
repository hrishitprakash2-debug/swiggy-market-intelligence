-- Q17 | Top 3 rated outlets in each of the largest localities (RANK + partition)
-- Business question: who is actually winning consumer ratings in the biggest markets?
WITH big AS (
    SELECT locality_sk FROM fact_listing GROUP BY locality_sk
    ORDER BY COUNT(*) DESC LIMIT 6
),
rated AS (
    SELECT f.listing_id, f.restaurant, l.locality_name, c.city_name,
           f.rating, f.rating_count, f.cost_for_two,
           RANK() OVER (PARTITION BY f.locality_sk
                        ORDER BY f.rating DESC, f.rating_count DESC) AS rnk
    FROM fact_listing f
    JOIN dim_locality l ON l.locality_sk = f.locality_sk
    JOIN dim_city     c ON c.city_sk     = l.city_sk
    WHERE f.locality_sk IN (SELECT locality_sk FROM big)
      AND f.rating IS NOT NULL
      AND f.rating_count >= 200
)
SELECT city_name, locality_name, rnk, restaurant, rating, rating_count, cost_for_two
FROM rated
WHERE rnk <= 3
ORDER BY locality_name, rnk;
