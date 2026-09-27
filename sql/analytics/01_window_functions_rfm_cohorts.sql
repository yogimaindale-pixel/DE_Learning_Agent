-- Window Functions & RFM Customer Segment Ranks
-- Calculates customer spend ranks, dense ranks, lag prior order dates, and lead order gaps.

WITH CustomerSpend AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.city,
        COUNT(f.order_id) AS total_orders,
        SUM(f.net_amount) AS total_spend,
        MAX(d.full_date) AS last_order_date
    FROM fact_order_item f
    JOIN dim_customer c ON f.customer_sk = c.customer_sk
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY c.customer_id, c.first_name, c.last_name, c.city
)
SELECT 
    customer_id,
    customer_name,
    city,
    total_orders,
    total_spend,
    last_order_date,
    ROW_NUMBER() OVER (ORDER BY total_spend DESC) AS spend_row_num,
    RANK() OVER (ORDER BY total_spend DESC) AS spend_rank,
    DENSE_RANK() OVER (ORDER BY total_spend DESC) AS spend_dense_rank,
    NTILE(4) OVER (ORDER BY total_spend DESC) AS spend_quartile
FROM CustomerSpend;
