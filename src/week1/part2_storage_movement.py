import json
import hashlib
import pandas as pd
from typing import Dict, Any, List
from src.config import DATA_DIR, DB_PATH
from src.database import get_connection, query_db, execute_query
from src.logging_utils import logger, generate_run_id

def run_part2_demos() -> Dict[str, Any]:
    logger.info("Running Week 1 Part 2 Storage & Movement Demos...")
    return {
        "medallion_pipeline": demo_medallion_storage_pipeline(),
        "file_formats": demo_file_format_comparison(),
        "saas_normalization": demo_saas_connector_normalization()
    }

def demo_medallion_storage_pipeline() -> Dict[str, Any]:
    """Demonstrates Raw/Bronze -> Staging/Silver -> Curated/Gold transformation"""
    run_id = generate_run_id()
    
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Bronze -> Silver Customers
    bronze_cust = cur.execute("SELECT customer_id, first_name, last_name, email, phone, city, state, created_at, updated_at FROM bronze_customers;").fetchall()
    silver_loaded = 0
    
    cust_params = []
    for c in bronze_cust:
        if not c["customer_id"] or not c["email"]:
            continue
            
        full_name = f"{c['first_name']} {c['last_name']}"
        email_parts = c["email"].split("@")
        masked_email = f"{email_parts[0][0]}***@{email_parts[1]}" if len(email_parts) == 2 else "***@example.com"
        phone_str = str(c["phone"]) if c["phone"] else ""
        masked_phone = f"******{phone_str[-4:]}" if len(phone_str) >= 4 else "******"
        email_hash = hashlib.sha256(c["email"].encode("utf-8")).hexdigest()
        
        cust_params.append((c["customer_id"], full_name, masked_email, masked_phone, email_hash, c["city"], c["state"], c["created_at"], c["updated_at"]))
        silver_loaded += 1
        
    cur.executemany("""
        INSERT INTO silver_customers (customer_id, full_name, masked_email, masked_phone, email_hash, city, state, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(customer_id) DO UPDATE SET
            full_name = excluded.full_name,
            masked_email = excluded.masked_email,
            updated_at = excluded.updated_at;
    """, cust_params)
    
    # 2. Bronze -> Silver Orders
    bronze_orders = cur.execute("SELECT order_id, customer_id, store_id, order_status, total_amount, created_at, updated_at FROM bronze_orders;").fetchall()
    silver_orders_count = 0
    order_params = []
    for o in bronze_orders:
        if o["order_id"] is None or o["total_amount"] < 0:
            continue
        order_date = o["created_at"].split(" ")[0] if o["created_at"] else "1900-01-01"
        order_params.append((o["order_id"], o["customer_id"], o["store_id"], o["order_status"], o["total_amount"], order_date, o["created_at"], o["updated_at"]))
        silver_orders_count += 1
        
    cur.executemany("""
        INSERT INTO silver_orders (order_id, customer_id, store_id, order_status, total_amount, order_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(order_id) DO UPDATE SET
            order_status = excluded.order_status,
            total_amount = excluded.total_amount,
            updated_at = excluded.updated_at;
    """, order_params)
    
    # 3. Silver -> Gold Daily Sales Summary
    cur.execute("""
        INSERT INTO gold_daily_sales_summary (summary_date, store_id, total_orders, successful_orders, total_revenue, avg_order_value)
        SELECT 
            order_date as summary_date,
            store_id,
            COUNT(order_id) as total_orders,
            SUM(CASE WHEN order_status = 'DELIVERED' THEN 1 ELSE 0 END) as successful_orders,
            SUM(CASE WHEN order_status = 'DELIVERED' THEN total_amount ELSE 0 END) as total_revenue,
            AVG(CASE WHEN order_status = 'DELIVERED' THEN total_amount ELSE 0 END) as avg_order_value
        FROM silver_orders
        GROUP BY order_date, store_id
        ON CONFLICT(summary_date, store_id) DO UPDATE SET
            total_orders = excluded.total_orders,
            successful_orders = excluded.successful_orders,
            total_revenue = excluded.total_revenue,
            avg_order_value = excluded.avg_order_value,
            updated_at = CURRENT_TIMESTAMP;
    """)
    
    gold_rows = cur.execute("SELECT COUNT(*) as cnt FROM gold_daily_sales_summary;").fetchone()["cnt"]
    conn.commit()
    conn.close()
    
    return {
        "lab": "Medallion Pipeline Execution",
        "silver_customers": silver_loaded,
        "silver_orders": silver_orders_count,
        "gold_summary_rows": gold_rows
    }

def demo_file_format_comparison() -> Dict[str, Any]:
    raw_csv = DATA_DIR / "raw" / "customers.csv"
    df = pd.read_csv(raw_csv)
    
    parquet_path = DATA_DIR / "staging" / "customers.parquet"
    json_path = DATA_DIR / "staging" / "customers.json"
    
    df.to_parquet(parquet_path, index=False)
    df.to_json(json_path, orient="records", indent=2)
    
    csv_size = raw_csv.stat().st_size
    parquet_size = parquet_path.stat().st_size
    json_size = json_path.stat().st_size
    
    return {
        "lab": "File Format Benchmark",
        "csv_bytes": csv_size,
        "parquet_bytes": parquet_size,
        "json_bytes": json_size,
        "compression_ratio_parquet_vs_csv": round(csv_size / parquet_size, 2) if parquet_size > 0 else 1.0
    }

def demo_saas_connector_normalization() -> Dict[str, Any]:
    saas_file = DATA_DIR / "raw" / "saas_exports.json"
    with open(saas_file, "r", encoding="utf-8") as f:
        saas_data = json.load(f)
        
    canonical_employees = []
    for emp in saas_data:
        canonical_employees.append({
            "employee_id": emp["employee_id"],
            "full_name": emp["full_name"],
            "department": emp["department"],
            "is_active": 1,
            "source_system": "Salesforce/Workday_Export"
        })
        
    return {
        "lab": "SaaS Export Canonical Normalization",
        "processed_employees": len(canonical_employees)
    }
