-- SCD Type 2 Dimension History Merge Strategy
-- Expires active customer record when a city/state update occurs, and inserts a new current version.

-- Step 1: Expire old active records
UPDATE dim_customer
SET expiry_date = CURRENT_DATE,
    is_current = 0
WHERE customer_id IN (SELECT customer_id FROM staging_customer_changes)
  AND is_current = 1;

-- Step 2: Insert new active versions
INSERT INTO dim_customer (
    customer_id,
    first_name,
    last_name,
    email,
    city,
    state,
    effective_date,
    expiry_date,
    is_current,
    version
)
SELECT
    s.customer_id,
    s.first_name,
    s.last_name,
    s.email,
    s.city,
    s.state,
    CURRENT_DATE AS effective_date,
    NULL AS expiry_date,
    1 AS is_current,
    COALESCE((SELECT MAX(version) FROM dim_customer d WHERE d.customer_id = s.customer_id), 0) + 1 AS version
FROM staging_customer_changes s;
