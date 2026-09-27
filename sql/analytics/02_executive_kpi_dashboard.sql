-- Executive KPI Dashboard Analytics Query
-- Computes Gross Merchandise Value (GMV), Net Revenue, Average Order Value (AOV), and Order Fulfilment Rates.

SELECT 
    d.year,
    d.month_name,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.total_price), 2) AS gmv,
    ROUND(SUM(f.discount_amount), 2) AS total_discounts,
    ROUND(SUM(f.net_amount), 2) AS net_revenue,
    ROUND(AVG(f.net_amount), 2) AS average_order_value
FROM fact_order_item f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year DESC, d.month DESC;
