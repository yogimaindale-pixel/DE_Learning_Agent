-- Bronze Layer (Raw Ingestion Tables)
CREATE TABLE IF NOT EXISTS bronze_customers (
    raw_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    city TEXT,
    state TEXT,
    created_at TEXT,
    updated_at TEXT,
    ingested_at TEXT DEFAULT CURRENT_TIMESTAMP,
    input_file TEXT
);

CREATE TABLE IF NOT EXISTS bronze_orders (
    raw_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    customer_id INTEGER,
    store_id INTEGER,
    order_status TEXT,
    total_amount REAL,
    created_at TEXT,
    updated_at TEXT,
    ingested_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bronze_payments (
    raw_id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id TEXT,
    order_id INTEGER,
    payment_method TEXT,
    payment_status TEXT,
    amount REAL,
    card_last4 TEXT,
    created_at TEXT,
    ingested_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Silver Layer (Cleaned, Standardized, Masked Tables)
CREATE TABLE IF NOT EXISTS silver_customers (
    customer_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    masked_email TEXT NOT NULL,
    masked_phone TEXT,
    email_hash TEXT NOT NULL,
    city TEXT,
    state TEXT,
    created_at TEXT,
    updated_at TEXT,
    processed_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver_orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    order_status TEXT NOT NULL,
    total_amount REAL NOT NULL,
    order_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    processed_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver_payments (
    payment_id TEXT PRIMARY KEY,
    order_id INTEGER NOT NULL,
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    amount REAL NOT NULL,
    processed_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Gold Layer (Business Aggregates / Curated Data)
CREATE TABLE IF NOT EXISTS gold_daily_sales_summary (
    summary_date TEXT NOT NULL,
    store_id INTEGER NOT NULL,
    total_orders INTEGER NOT NULL,
    successful_orders INTEGER NOT NULL,
    total_revenue REAL NOT NULL,
    avg_order_value REAL NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (summary_date, store_id)
);

CREATE TABLE IF NOT EXISTS gold_customer_spend_summary (
    customer_id INTEGER PRIMARY KEY,
    total_orders INTEGER NOT NULL,
    lifetime_spend REAL NOT NULL,
    first_order_date TEXT,
    last_order_date TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
