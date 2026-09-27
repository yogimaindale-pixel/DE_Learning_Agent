-- Dimensions
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_sk INTEGER PRIMARY KEY AUTOINCREMENT, -- Surrogate Key
    customer_id INTEGER NOT NULL, -- Business Key
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    city TEXT,
    state TEXT,
    effective_date TEXT NOT NULL,
    expiry_date TEXT,
    is_current INTEGER DEFAULT 1,
    version INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    current_price REAL NOT NULL,
    previous_category TEXT, -- SCD Type 3
    effective_date TEXT NOT NULL,
    is_current INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS dim_store (
    store_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id INTEGER NOT NULL,
    store_name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY, -- YYYYMMDD
    full_date TEXT NOT NULL,
    day_of_week TEXT NOT NULL,
    day_name TEXT NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    is_weekend INTEGER NOT NULL
);

-- Prescription Analytics Dimension (Lenskart Capstone Requirement)
CREATE TABLE IF NOT EXISTS dim_prescription (
    prescription_sk INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    sphere_left REAL NOT NULL,
    sphere_right REAL NOT NULL,
    cylinder_left REAL,
    cylinder_right REAL,
    lens_type TEXT NOT NULL, -- Single Vision, Bifocal, Progressive
    created_at TEXT NOT NULL
);

-- Fact Tables
CREATE TABLE IF NOT EXISTS fact_order_item (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    customer_sk INTEGER NOT NULL,
    product_sk INTEGER NOT NULL,
    store_sk INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    discount_amount REAL DEFAULT 0.0,
    net_amount REAL NOT NULL,
    FOREIGN KEY (customer_sk) REFERENCES dim_customer(customer_sk),
    FOREIGN KEY (product_sk) REFERENCES dim_product(product_sk),
    FOREIGN KEY (store_sk) REFERENCES dim_store(store_sk),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE TABLE IF NOT EXISTS fact_daily_sales_snapshot (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_key INTEGER NOT NULL,
    store_sk INTEGER NOT NULL,
    total_orders INTEGER NOT NULL,
    total_items_sold INTEGER NOT NULL,
    total_gross_revenue REAL NOT NULL,
    total_net_revenue REAL NOT NULL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (store_sk) REFERENCES dim_store(store_sk)
);

CREATE TABLE IF NOT EXISTS fact_delivery_lifecycle (
    delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    order_placed_ts TEXT NOT NULL,
    order_assigned_ts TEXT,
    order_picked_ts TEXT,
    order_delivered_ts TEXT,
    delivery_partner_id INTEGER,
    delivery_duration_minutes REAL,
    is_on_time INTEGER DEFAULT 1
);
