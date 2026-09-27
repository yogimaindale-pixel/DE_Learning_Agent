import hashlib
import sqlite3
from typing import Dict, Any, List
from src.database import get_connection, query_db, execute_query
from src.logging_utils import logger

def run_part2_demos() -> Dict[str, Any]:
    logger.info("Running Week 4 Part 2 Quality, Privacy & Performance Demos...")
    
    dq_res = demo_declarative_data_quality()
    privacy_res = demo_pii_vault_and_dpdp_gdpr()
    perf_res = demo_query_optimization_explain_plan()
    
    return {
        "data_quality_gates": dq_res,
        "pii_privacy_compliance": privacy_res,
        "performance_optimization": perf_res
    }

def demo_declarative_data_quality() -> Dict[str, Any]:
    """Declarative Data Quality as Code Gates"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Run DQ Check 1: Uniqueness of customer_id in silver_customers
    cur.execute("SELECT customer_id, COUNT(*) FROM silver_customers GROUP BY customer_id HAVING COUNT(*) > 1;")
    dups = cur.fetchall()
    dq1_passed = len(dups) == 0
    
    # Run DQ Check 2: No null emails in silver_customers
    cur.execute("SELECT COUNT(*) as cnt FROM silver_customers WHERE masked_email IS NULL OR masked_email = '';")
    null_emails = cur.fetchone()["cnt"]
    dq2_passed = null_emails == 0
    
    conn.close()
    
    return {
        "dq_check_1_uniqueness": "PASSED" if dq1_passed else "FAILED",
        "dq_check_2_not_null": "PASSED" if dq2_passed else "FAILED"
    }

def demo_pii_vault_and_dpdp_gdpr() -> Dict[str, Any]:
    """PII Vault Pattern & DPDP/GDPR Compliance Demonstration"""
    raw_email = "customer.pii@example.com"
    raw_phone = "+919876543210"
    
    # Hashing & Masking
    masked_email = f"c***i@example.com"
    masked_phone = "******3210"
    email_hash = hashlib.sha256(raw_email.encode("utf-8")).hexdigest()
    
    compliance_principles = [
        "1. Data Minimization: Store only required fields in Silver/Gold layers",
        "2. Anonymization & Pseudonymization: SHA-256 Hashing and Tokenization",
        "3. Column Masking: Mask email addresses and phone numbers",
        "4. Least Privilege Access: Restrict Bronze raw access; expose Gold aggregates without PII",
        "5. Right to Erasure / Forgotten: Token vault deletion invalidates historic references without breaking aggregate metrics"
    ]
    
    return {
        "lab": "PII Vault & DPDP/GDPR Compliance Pattern",
        "raw_email": raw_email,
        "masked_email": masked_email,
        "sha256_hash": email_hash,
        "compliance_principles": compliance_principles
    }

def demo_query_optimization_explain_plan() -> Dict[str, Any]:
    """Query Profiling with EXPLAIN QUERY PLAN and Index Optimization"""
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. EXPLAIN QUERY PLAN before index
    explain_before = cur.execute("EXPLAIN QUERY PLAN SELECT * FROM silver_orders WHERE customer_id = 42;").fetchall()
    before_text = [dict(r) for r in explain_before]
    
    # 2. Create index
    cur.execute("CREATE INDEX IF NOT EXISTS idx_silver_orders_cust ON silver_orders(customer_id);")
    conn.commit()
    
    # 3. EXPLAIN QUERY PLAN after index
    explain_after = cur.execute("EXPLAIN QUERY PLAN SELECT * FROM silver_orders WHERE customer_id = 42;").fetchall()
    after_text = [dict(r) for r in explain_after]
    
    conn.close()
    
    return {
        "explain_plan_before_index": before_text,
        "explain_plan_after_index": after_text,
        "performance_gain": "Switched from FULL TABLE SCAN to SEARCH INDEX using idx_silver_orders_cust"
    }
