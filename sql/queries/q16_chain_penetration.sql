-- Q16 | Chain penetration: brands operating in many localities
-- Business question: how chain-dominated is Swiggy supply, and where?
WITH brand AS (
    SELECT f.restaurant,
           COUNT(DISTINCT f.locality_sk)                AS localities_present,
           COUNT(*)                                     AS outlets,
           COUNT(DISTINCT l.city_sk)                    AS cities_present,
           ROUND(AVG(f.rating), 2)                      AS avg_rating,
           ROUND(AVG(f.cost_for_two), 0)                AS avg_cost
    FROM fact_listing f
    JOIN dim_locality l ON l.locality_sk = f.locality_sk
    GROUP BY f.restaurant
)
SELECT restaurant, outlets, localities_present, cities_present, avg_rating, avg_cost
FROM brand
WHERE outlets >= 8
ORDER BY outlets DESC, localities_present DESC
LIMIT 25;
