import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.config import DB_PATH, SQL_DIR, DATABASE_DIR
from src.logging_utils import logger

def get_connection() -> sqlite3.Connection:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db() -> None:
    logger.info("Initializing SQLite database and schema...")
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    
    if DB_PATH.exists():
        try:
            DB_PATH.unlink()
        except Exception:
            pass
            
    conn = get_connection()
    ddl_files = [
        "01_audit_tables.sql",
        "02_oltp_tables.sql",
        "03_medallion_tables.sql",
        "04_star_schema_tables.sql"
    ]
    
    for ddl in ddl_files:
        path = SQL_DIR / "ddl" / ddl
        if path.exists():
            logger.info(f"Executing DDL: {ddl}")
            with open(path, "r", encoding="utf-8") as f:
                sql_script = f.read()
            conn.executescript(sql_script)
            
    _ensure_unknown_members(conn)
    _ensure_pipeline_control_entries(conn)
    conn.commit()
    conn.close()
    logger.info("Database initialization complete.")

def execute_query(query: str, params: tuple = ()) -> None:
    conn = get_connection()
    try:
        conn.execute(query, params)
        conn.commit()
    finally:
        conn.close()

def query_db(query: str, params: tuple = ()) -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()

def _ensure_unknown_members(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO dim_customer (customer_sk, customer_id, first_name, last_name, email, city, state, effective_date, is_current, version)
        VALUES (-1, -1, 'Unknown', 'Customer', 'unknown@domain.com', 'Unknown', 'Unknown', '1900-01-01', 1, 1)
        ON CONFLICT(customer_sk) DO NOTHING;
    """)
    cursor.execute("""
        INSERT INTO dim_product (product_sk, product_id, product_name, category, current_price, effective_date, is_current)
        VALUES (-1, -1, 'Unknown Product', 'Unknown', 0.0, '1900-01-01', 1)
        ON CONFLICT(product_sk) DO NOTHING;
    """)
    cursor.execute("""
        INSERT INTO dim_store (store_sk, store_id, store_name, city, state)
        VALUES (-1, -1, 'Unknown Store', 'Unknown', 'Unknown')
        ON CONFLICT(store_sk) DO NOTHING;
    """)
    cursor.execute("""
        INSERT INTO dim_prescription (prescription_sk, prescription_id, customer_id, sphere_left, sphere_right, lens_type, created_at)
        VALUES (-1, -1, -1, 0.0, 0.0, 'Unknown', '1900-01-01 00:00:00')
        ON CONFLICT(prescription_sk) DO NOTHING;
    """)

def _ensure_pipeline_control_entries(conn: sqlite3.Connection) -> None:
    pipelines = [
        ("p001", "customers_ingestion", "sqlite_oltp", "bronze_customers"),
        ("p002", "orders_ingestion", "sqlite_oltp", "bronze_orders"),
        ("p003", "products_ingestion", "csv", "bronze_products"),
        ("p004", "payments_ingestion", "mock_api", "bronze_payments"),
        ("p005", "deliveries_ingestion", "kafka_ndjson", "bronze_deliveries"),
        ("p006", "saas_employee_ingestion", "json", "bronze_saas_employees"),
    ]
    cursor = conn.cursor()
    for pid, name, stype, target in pipelines:
        cursor.execute("""
            INSERT INTO pipeline_control (pipeline_id, pipeline_name, source_type, target_table, is_active)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(pipeline_id) DO NOTHING;
        """, (pid, name, stype, target))
