import json
import csv
import time
import random
import pandas as pd
from typing import Dict, Any, List
from src.config import DATA_DIR, DB_PATH
from src.database import get_connection, query_db, execute_query
from src.logging_utils import logger, generate_run_id

def run_part1_demos() -> Dict[str, Any]:
    logger.info("Running Week 1 Part 1 Demonstrations & Labs...")
    results = {}
    
    results["full_load"] = demo_full_load_csv()
    results["incremental_load"] = demo_incremental_load()
    results["cdc"] = demo_cdc_operations()
    results["streaming"] = demo_streaming_microbatch()
    results["rest_api"] = demo_mock_rest_api_pagination()
    results["decision_matrix"] = get_decision_matrix()
    
    return results

def demo_full_load_csv() -> Dict[str, Any]:
    """Lab 1: Full Load from customers CSV into Bronze SQLite table"""
    run_id = generate_run_id()
    csv_file = DATA_DIR / "raw" / "customers.csv"
    conn = get_connection()
    
    df = pd.read_csv(csv_file)
    extracted_count = len(df)
    
    valid_rows = []
    rejected_count = 0
    
    for idx, row in df.iterrows():
        if "@" not in str(row["email"]):
            rejected_count += 1
            conn.execute("""
                INSERT INTO rejected_records (run_id, pipeline_id, raw_payload, reason_code, error_details)
                VALUES (?, 'p001_csv', ?, 'INVALID_EMAIL', 'Email format check failed');
            """, (run_id, str(row.to_dict())))
        else:
            valid_rows.append(row)
            
    valid_df = pd.DataFrame(valid_rows)
    loaded_count = len(valid_df)
    
    valid_df.to_sql("bronze_customers", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
    
    return {
        "lab": "Full Load CSV -> Bronze",
        "scenario": "HDFC Regulated Core Ingestion",
        "extracted": extracted_count,
        "loaded": loaded_count,
        "rejected": rejected_count
    }

def demo_incremental_load() -> Dict[str, Any]:
    """Lab 2: Incremental orders load using updated_at watermark"""
    run_id = generate_run_id()
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT last_watermark FROM pipeline_control WHERE pipeline_id = 'p002';")
    row = cur.fetchone()
    last_wm = row["last_watermark"] if row and row["last_watermark"] else "1900-01-01 00:00:00"
    
    orders = cur.execute("""
        SELECT order_id, customer_id, store_id, order_status, total_amount, created_at, updated_at
        FROM oltp_orders
        WHERE updated_at > ?
        ORDER BY updated_at ASC;
    """, (last_wm,)).fetchall()
    
    extracted_count = len(orders)
    loaded_count = 0
    rejected_count = 0
    max_updated_at = last_wm
    
    valid_orders = []
    for o in orders:
        if o["total_amount"] < 0:
            rejected_count += 1
            cur.execute("""
                INSERT INTO rejected_records (run_id, pipeline_id, raw_payload, reason_code, error_details)
                VALUES (?, 'p002', ?, 'NEGATIVE_AMOUNT', 'Order total amount is negative');
            """, (run_id, str(dict(o))))
        else:
            valid_orders.append((o["order_id"], o["customer_id"], o["store_id"], o["order_status"], o["total_amount"], o["created_at"], o["updated_at"]))
            loaded_count += 1
            if o["updated_at"] > max_updated_at:
                max_updated_at = o["updated_at"]
                
    cur.executemany("""
        INSERT INTO bronze_orders (order_id, customer_id, store_id, order_status, total_amount, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, valid_orders)
    
    if loaded_count > 0:
        cur.execute("""
            UPDATE pipeline_control
            SET last_watermark = ?, updated_at = CURRENT_TIMESTAMP
            WHERE pipeline_id = 'p002';
        """, (max_updated_at,))
        
    conn.commit()
    conn.close()
    
    return {
        "lab": "Incremental Load with Watermark",
        "scenario": "Meesho E-Commerce Incremental Orders",
        "previous_watermark": last_wm,
        "new_watermark": max_updated_at,
        "extracted": extracted_count,
        "loaded": loaded_count,
        "rejected": rejected_count
    }

def demo_cdc_operations() -> Dict[str, Any]:
    """Lab 3: CDC Ingestion with Insert (I), Update (U), and Delete (D) operation codes"""
    cdc_events = [
        {"op": "I", "customer_id": 501, "first_name": "Rohan", "last_name": "Sharma", "email": "rohan@example.com", "ts": "2024-06-01 10:00:00"},
        {"op": "U", "customer_id": 501, "first_name": "Rohan", "last_name": "Sharma", "email": "rohan.sharma@example.com", "ts": "2024-06-01 10:15:00"},
        {"op": "D", "customer_id": 501, "ts": "2024-06-01 11:00:00"}
    ]
    
    applied = 0
    conn = get_connection()
    cur = conn.cursor()
    for evt in cdc_events:
        if evt["op"] == "I":
            cur.execute("""
                INSERT INTO bronze_customers (customer_id, first_name, last_name, email, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (evt["customer_id"], evt["first_name"], evt["last_name"], evt["email"], evt["ts"], evt["ts"]))
            applied += 1
        elif evt["op"] == "U":
            cur.execute("""
                UPDATE bronze_customers
                SET email = ?, updated_at = ?
                WHERE customer_id = ?;
            """, (evt["email"], evt["ts"], evt["customer_id"]))
            applied += 1
        elif evt["op"] == "D":
            cur.execute("DELETE FROM bronze_customers WHERE customer_id = ?;", (evt["customer_id"],))
            applied += 1
            
    conn.commit()
    conn.close()
    return {
        "lab": "CDC Event Stream",
        "events_processed": len(cdc_events),
        "applied_ops": applied
    }

def demo_streaming_microbatch() -> Dict[str, Any]:
    """Lab 4: Streaming Micro-batch from Kafka NDJSON file"""
    ndjson_file = DATA_DIR / "raw" / "delivery_stream.ndjson"
    batch_records = []
    
    with open(ndjson_file, "r", encoding="utf-8") as f:
        for line in f:
            batch_records.append(json.loads(line.strip()))
            
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bronze_deliveries (
            delivery_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            status TEXT,
            delivery_partner_id INTEGER,
            delivery_address TEXT,
            timestamp TEXT
        );
    """)
    for r in batch_records:
        cur.execute("""
            INSERT OR REPLACE INTO bronze_deliveries (delivery_id, order_id, status, delivery_partner_id, delivery_address, timestamp)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (r["delivery_id"], r["order_id"], r["status"], r["delivery_partner_id"], r["delivery_address"], r["timestamp"]))
    conn.commit()
    conn.close()
    
    return {
        "lab": "Streaming Micro-batch NDJSON",
        "scenario": "Swiggy/Zepto Real-Time Delivery Tracking",
        "processed_records": len(batch_records)
    }

def demo_mock_rest_api_pagination() -> Dict[str, Any]:
    """Lab 5: Paginated REST API mock with Rate Limit (429) simulation and Exponential Backoff"""
    pages = ["mock_payments_api_page1.json", "mock_payments_api_page2.json"]
    extracted_records = []
    attempts = 0
    retries = 0
    
    for page_file in pages:
        filepath = DATA_DIR / "raw" / page_file
        attempts += 1
        if page_file == "mock_payments_api_page2.json" and retries == 0:
            logger.info("Simulating HTTP 429 Rate Limit encountered. Applying exponential backoff...")
            retries += 1
            time.sleep(0.01)
            
        with open(filepath, "r", encoding="utf-8") as f:
            payload = json.load(f)
            extracted_records.extend(payload["data"])
            
    return {
        "lab": "Paginated REST API & Rate Limit Handling",
        "scenario": "Stripe/Razorpay API Integration",
        "pages_fetched": len(pages),
        "total_records_extracted": len(extracted_records),
        "rate_limit_retries": retries
    }

def get_decision_matrix() -> List[Dict[str, Any]]:
    return [
        {"pattern": "Full Load", "volume": "Small (< 100K rows)", "latency": "Batch (Daily/Weekly)", "replay_need": "High", "use_case": "Dim tables, Master data"},
        {"pattern": "Incremental Load", "volume": "Medium/Large (> 1M rows)", "latency": "Hourly/Daily", "replay_need": "Medium", "use_case": "Transactional orders with updated_at"},
        {"pattern": "CDC (Log-based)", "volume": "Large (High Throughput)", "latency": "Near Real-Time (< 1 min)", "replay_need": "High", "use_case": "OLTP database replication"},
        {"pattern": "Streaming", "volume": "Continuous event streams", "latency": "Sub-second", "replay_need": "Configurable (Kafka topic)", "use_case": "Clickstream, GPS tracking (Swiggy, Zepto)"}
    ]
