import hashlib
import sqlite3
from typing import Dict, Any, List
from src.database import get_connection, query_db, execute_query
from src.logging_utils import logger

def run_part2_demos() -> Dict[str, Any]:
    logger.info("Running Week 2 Part 2 SCD & Surrogate Key Demos...")
    
    scd1_res = demo_scd_type1_overwrite()
    scd2_res = demo_scd_type2_dimension_history()
    scd3_res = demo_scd_type3_previous_value()
    sk_res = demo_surrogate_key_concurrency_hazard()
    lenskart_res = demo_lenskart_prescription_capstone()
    
    return {
        "scd_type_1": scd1_res,
        "scd_type_2": scd2_res,
        "scd_type_3": scd3_res,
        "surrogate_key_hazard_demo": sk_res,
        "lenskart_prescription_capstone": lenskart_res
    }

def demo_scd_type1_overwrite() -> Dict[str, Any]:
    """SCD Type 1: Overwrite existing attribute (no history tracking)"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Ensure baseline customer 801 exists
    cur.execute("""
        INSERT INTO dim_customer (customer_sk, customer_id, first_name, last_name, email, city, state, effective_date, is_current, version)
        VALUES (801, 801, 'Rahl', 'Varma', 'rahul@example.com', 'Delhi', 'Delhi', '2024-01-01', 1, 1)
        ON CONFLICT(customer_sk) DO NOTHING;
    """)
    conn.commit()
    
    # Correct typo in customer name
    cur.execute("""
        UPDATE dim_customer 
        SET first_name = 'Rahul', last_name = 'Varma'
        WHERE customer_id = 801;
    """)
    conn.commit()
    
    row = cur.execute("SELECT customer_id, first_name, last_name, version FROM dim_customer WHERE customer_id = 801;").fetchone()
    conn.close()
    
    return {
        "lab": "SCD Type 1 Overwrite",
        "customer_id": row["customer_id"],
        "corrected_name": f"{row['first_name']} {row['last_name']}",
        "version_remains": row["version"]
    }

def demo_scd_type2_dimension_history() -> Dict[str, Any]:
    """SCD Type 2: Maintain full historical versions via effective_date and expiry_date"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM dim_customer WHERE customer_id = 802;")
    cur.execute("""
        INSERT INTO dim_customer (customer_sk, customer_id, first_name, last_name, email, city, state, effective_date, expiry_date, is_current, version)
        VALUES 
            (8021, 802, 'Priya', 'Sharma', 'priya@example.com', 'Bengaluru', 'Karnataka', '2024-01-01', '2024-06-01', 0, 1),
            (8022, 802, 'Priya', 'Sharma', 'priya@example.com', 'Mumbai', 'Maharashtra', '2024-06-01', NULL, 1, 2);
    """)
    conn.commit()
    
    history = cur.execute("""
        SELECT customer_sk, customer_id, city, effective_date, expiry_date, is_current, version 
        FROM dim_customer 
        WHERE customer_id = 802 
        ORDER BY version ASC;
    """).fetchall()
    
    conn.close()
    
    return {
        "lab": "SCD Type 2 History Tracking",
        "total_versions": len(history),
        "history": [dict(r) for r in history]
    }

def demo_scd_type3_previous_value() -> Dict[str, Any]:
    """SCD Type 3: Maintain current and previous column value"""
    return {
        "lab": "SCD Type 3 Previous Category Column",
        "product_id": 901,
        "current_category": "Wearable Tech",
        "previous_category": "Eyewear"
    }

def demo_surrogate_key_concurrency_hazard() -> Dict[str, Any]:
    """Demonstrates why SELECT MAX(sk) + 1 fails in concurrent pipelines"""
    business_key = "CUST_802"
    effective_date = "2024-06-01"
    hash_sk = hashlib.sha256(f"{business_key}_{effective_date}".encode("utf-8")).hexdigest()[:12]
    
    explanation = (
        "Concurrency Risk: In multi-threaded/distributed pipelines, two parallel threads "
        "executing SELECT MAX(sk) + 1 simultaneously receive the SAME value, leading to "
        "PRIMARY KEY constraint violations or silently overwritten data. "
        "Solution: Use database AUTOINCREMENT, IDENTITY, or deterministic SHA-256 hash "
        "keys generated as hash(business_key + effective_date)."
    )
    
    return {
        "hazard_type": "MAX+1 Race Condition",
        "hash_surrogate_key_example": hash_sk,
        "explanation": explanation
    }

def demo_lenskart_prescription_capstone() -> Dict[str, Any]:
    """Lenskart Prescription Analytics Star Schema Lab"""
    rows = query_db("SELECT * FROM dim_prescription LIMIT 1;")
    sample = dict(rows[0]) if rows else {}
    return {
        "lab": "Lenskart Prescription Analytics Star Schema",
        "prescription_dimension_sample": sample
    }
