-- Silver to Gold Aggregation Transformation
-- Aggregates daily order sales by store, date, and state for executive analytics dashboards.

INSERT INTO gold_daily_store_sales (
    date_key,
    store_sk,
    store_name,
    state,
    total_orders,
    total_items_sold,
    gross_revenue,
    net_revenue
)
SELECT
    f.date_key,
    f.store_sk,
    s.store_name,
    s.state,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_items_sold,
    SUM(f.total_price) AS gross_revenue,
    SUM(f.net_amount) AS net_revenue
FROM fact_order_item f
JOIN dim_store s ON f.store_sk = s.store_sk
GROUP BY f.date_key, f.store_sk, s.store_name, s.state;
