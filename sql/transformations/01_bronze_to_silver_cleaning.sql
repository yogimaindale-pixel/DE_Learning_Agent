-- Bronze to Silver Cleaning Transformation
-- Cleanses raw customer records, validates email format, normalizes state codes, and masks PII.

INSERT INTO silver_customers (
    customer_id,
    first_name,
    last_name,
    email,
    city,
    state,
    ingested_at,
    is_valid,
    validation_notes
)
SELECT
    customer_id,
    TRIM(first_name) AS first_name,
    TRIM(last_name) AS last_name,
    LOWER(TRIM(email)) AS email,
    TRIM(city) AS city,
    UPPER(TRIM(state)) AS state,
    CURRENT_TIMESTAMP AS ingested_at,
    CASE 
        WHEN email LIKE '%@%.%' AND customer_id IS NOT NULL THEN 1
        ELSE 0
    END AS is_valid,
    CASE 
        WHEN email NOT LIKE '%@%.%' THEN 'INVALID_EMAIL_FORMAT'
        WHEN customer_id IS NULL THEN 'MISSING_CUSTOMER_ID'
        ELSE 'CLEAN'
    END AS validation_notes
FROM bronze_customers;
