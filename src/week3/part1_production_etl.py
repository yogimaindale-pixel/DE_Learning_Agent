import time
import json
import sqlite3
from typing import Dict, Any, List
from src.database import get_connection, query_db, execute_query
from src.logging_utils import logger, generate_run_id

def run_part1_demos() -> Dict[str, Any]:
    logger.info("Running Week 3 Part 1 Production Pipeline & Error Handling Demos...")
    
    load_patterns = demo_pipeline_load_patterns()
    retry_dlq = demo_exponential_backoff_and_dlq()
    dlq_replay = demo_dlq_correction_and_replay()
    
    return {
        "load_patterns_comparison": load_patterns,
        "retry_and_dlq_isolation": retry_dlq,
        "dlq_replay": dlq_replay
    }

def demo_pipeline_load_patterns() -> Dict[str, Any]:
    """Compares Append-Only, Upsert/Merge, and Full Swap load strategies"""
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Append-Only (e.g. Audit Logs)
    cur.execute("""
        INSERT INTO pipeline_run_audit (run_id, pipeline_id, status, records_extracted, records_loaded, start_time)
        VALUES (?, 'p001', 'SUCCESS', 100, 100, CURRENT_TIMESTAMP);
    """, (generate_run_id(),))
    
    # 2. Upsert/Merge (SQLite INSERT ... ON CONFLICT DO UPDATE)
    cur.execute("""
        INSERT INTO silver_orders (order_id, customer_id, store_id, order_status, total_amount, order_date, created_at, updated_at)
        VALUES (1, 101, 1, 'DELIVERED', 1500.0, '2024-06-01', '2024-06-01 10:00:00', '2024-06-01 12:00:00')
        ON CONFLICT(order_id) DO UPDATE SET
            order_status = excluded.order_status,
            total_amount = excluded.total_amount,
            updated_at = excluded.updated_at;
    """)
    
    # 3. Full Swap (Atomic Table Swap via Transaction)
    cur.execute("CREATE TABLE IF NOT EXISTS staging_swap_test (id INT PRIMARY KEY, val TEXT);")
    cur.execute("DELETE FROM staging_swap_test;")
    cur.execute("INSERT INTO staging_swap_test VALUES (1, 'New Version A');")
    
    conn.commit()
    conn.close()
    
    return {
        "append_only": "Audit log inserted",
        "upsert_merge": "Order #1 idempotently merged",
        "full_swap": "Staging table refreshed"
    }

def demo_exponential_backoff_and_dlq() -> Dict[str, Any]:
    """Demonstrates Transient error retries and Data error isolation to DLQ"""
    run_id = generate_run_id()
    
    # 1. Transient Error Simulation with Retries & Exponential Backoff
    max_retries = 3
    retry_delay = 0.05
    transient_success = False
    
    for attempt in range(1, max_retries + 1):
        try:
            if attempt < 2:
                raise ConnectionError("Simulated network timeout connecting to REST API")
            transient_success = True
            break
        except ConnectionError as e:
            logger.warning(f"Transient error on attempt {attempt}/{max_retries}: {e}. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)
            retry_delay *= 2
            
    # 2. Data Error Isolation to Dead Letter Queue (DLQ)
    bad_rows = [
        {"order_id": 9901, "amount": -500.0, "reason": "NEGATIVE_AMOUNT"},
        {"order_id": 9902, "amount": 1200.0, "customer_id": None, "reason": "MISSING_PK"}
    ]
    
    conn = get_connection()
    cur = conn.cursor()
    for row in bad_rows:
        cur.execute("""
            INSERT INTO rejected_records (run_id, pipeline_id, raw_payload, reason_code, error_details)
            VALUES (?, 'p002', ?, ?, 'Data error isolated to DLQ');
        """, (run_id, json.dumps(row), row["reason"]))
    conn.commit()
    
    dlq_count = cur.execute("SELECT COUNT(*) as cnt FROM rejected_records WHERE run_id = ?;", (run_id,)).fetchone()["cnt"]
    conn.close()
    
    return {
        "transient_retry_success": transient_success,
        "attempts_made": attempt,
        "dlq_isolated_records": dlq_count
    }

def demo_dlq_correction_and_replay() -> Dict[str, Any]:
    """Demonstrates picking up DLQ items, fixing payload, and replaying pipeline"""
    conn = get_connection()
    cur = conn.cursor()
    
    dlq_item = cur.execute("SELECT reject_id, raw_payload FROM rejected_records LIMIT 1;").fetchone()
    if not dlq_item:
        conn.close()
        return {"replayed": False, "msg": "No DLQ items found"}
        
    payload = json.loads(dlq_item["raw_payload"])
    # Correct error
    if "amount" in payload and payload["amount"] < 0:
        payload["amount"] = abs(payload["amount"])
        
    # Replay into silver
    cur.execute("""
        INSERT INTO silver_orders (order_id, customer_id, store_id, order_status, total_amount, order_date, created_at, updated_at)
        VALUES (?, 1, 1, 'REPLAYED', ?, '2024-06-01', '2024-06-01 00:00:00', '2024-06-01 00:00:00')
        ON CONFLICT(order_id) DO UPDATE SET total_amount = excluded.total_amount;
    """, (payload["order_id"], payload["amount"]))
    
    conn.commit()
    conn.close()
    
    return {
        "replayed": True,
        "reject_id": dlq_item["reject_id"],
        "corrected_payload": payload
    }
