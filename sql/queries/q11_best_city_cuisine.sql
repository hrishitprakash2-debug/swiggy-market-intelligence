-- Q11 | Best-performing cuisine in each city (RANK partitioned by city)
-- Business question: which cuisine wins consumer satisfaction city by city?
WITH pairs AS (
    SELECT c.city_name, cu.cuisine_name,
           COUNT(*) AS listings,
           ROUND(AVG(f.rating), 3) AS avg_rating,
           ROUND(AVG(f.rating_count), 0) AS avg_reviews
    FROM fact_listing f
    JOIN dim_locality l ON l.locality_sk = f.locality_sk
    JOIN dim_city     c ON c.city_sk     = l.city_sk
    JOIN dim_cuisine cu ON cu.cuisine_sk = f.cuisine_sk
    WHERE f.rating IS NOT NULL
    GROUP BY c.city_name, cu.cuisine_name
    HAVING COUNT(*) >= 40
),
ranked AS (
    SELECT *, RANK() OVER (PARTITION BY city_name ORDER BY avg_rating DESC) AS rnk
    FROM pairs
)
SELECT city_name, rnk, cuisine_name, listings, avg_rating, avg_reviews
FROM ranked r
WHERE rnk <= 3
  AND EXISTS (SELECT 1 FROM (SELECT city_name FROM fact_listing f
                             JOIN dim_locality l ON l.locality_sk=f.locality_sk
                             JOIN dim_city c ON c.city_sk=l.city_sk
                             GROUP BY c.city_name HAVING COUNT(*) >= 300) big
              WHERE big.city_name = r.city_name)
ORDER BY city_name, rnk;
