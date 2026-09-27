-- Data Quality Gate: Null & Duplicate Checks

-- Check 1: Primary Key Uniqueness on dim_customer
SELECT 'dim_customer_pk_duplicates' AS check_name, COUNT(*) - COUNT(DISTINCT customer_sk) AS violation_count
FROM dim_customer;

-- Check 2: Mandatory NOT NULL attributes on fact_order_item
SELECT 'fact_order_item_null_fk' AS check_name, COUNT(*) AS violation_count
FROM fact_order_item
WHERE customer_sk IS NULL OR product_sk IS NULL OR store_sk IS NULL OR date_key IS NULL;

-- Check 3: Negative Price/Quantity Anomalies
SELECT 'fact_negative_quantity_price' AS check_name, COUNT(*) AS violation_count
FROM fact_order_item
WHERE quantity <= 0 OR unit_price < 0 OR total_price < 0;
