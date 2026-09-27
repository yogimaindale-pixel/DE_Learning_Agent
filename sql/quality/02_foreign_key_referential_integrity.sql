-- Data Quality Gate: Foreign Key Referential Integrity Checks

-- Verify all fact_order_item records join to valid customer dimensions
SELECT 'orphan_fact_customer_sk' AS check_name, COUNT(*) AS orphan_count
FROM fact_order_item f
LEFT JOIN dim_customer c ON f.customer_sk = c.customer_sk
WHERE c.customer_sk IS NULL;

-- Verify all fact_order_item records join to valid product dimensions
SELECT 'orphan_fact_product_sk' AS check_name, COUNT(*) AS orphan_count
FROM fact_order_item f
LEFT JOIN dim_product p ON f.product_sk = p.product_sk
WHERE p.product_sk IS NULL;

-- Verify all fact_order_item records join to valid date dimensions
SELECT 'orphan_fact_date_key' AS check_name, COUNT(*) AS orphan_count
FROM fact_order_item f
LEFT JOIN dim_date d ON f.date_key = d.date_key
WHERE d.date_key IS NULL;
