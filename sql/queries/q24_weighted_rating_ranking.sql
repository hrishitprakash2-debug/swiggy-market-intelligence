-- Q24 | Bayesian-weighted ranking — why a 5.0 from 20 reviews is not the best outlet
-- Business question: which outlets are genuinely best once review volume is priced in?
-- weighted = (rating * reviews + prior_rating * C) / (reviews + C), C = 150
WITH prior AS (
    SELECT AVG(rating) AS global_rating FROM fact_listing WHERE rating IS NOT NULL
),
scored AS (
    SELECT f.restaurant, l.locality_name, c.city_name, cu.cuisine_name,
           f.rating, f.rating_count, f.cost_for_two,
           ROUND((f.rating * f.rating_count + p.global_rating * 150.0)
                 / (f.rating_count + 150.0), 3)               AS weighted_rating,
           RANK() OVER (ORDER BY f.rating DESC, f.rating_count DESC) AS raw_rank
    FROM fact_listing f
    CROSS JOIN prior p
    JOIN dim_locality l ON l.locality_sk = f.locality_sk
    JOIN dim_city     c ON c.city_sk     = l.city_sk
    JOIN dim_cuisine cu ON cu.cuisine_sk = f.cuisine_sk
    WHERE f.rating IS NOT NULL AND f.rating_count >= 50
)
SELECT
    RANK() OVER (ORDER BY weighted_rating DESC) AS weighted_rank,
    restaurant, city_name, locality_name, cuisine_name,
    rating, rating_count, weighted_rating, raw_rank,
    raw_rank - RANK() OVER (ORDER BY weighted_rating DESC) AS rank_shift_vs_raw
FROM scored
ORDER BY weighted_rating DESC
LIMIT 20;
