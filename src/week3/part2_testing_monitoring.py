import pandera as pa
import pandas as pd
from typing import Dict, Any, List
from src.database import get_connection, query_db, execute_query
from src.logging_utils import logger

def run_part2_demos() -> Dict[str, Any]:
    logger.info("Running Week 3 Part 2 Testing, Monitoring & SLA Demos...")
    
    contract_res = demo_pandera_contract_testing()
    sla_res = demo_sla_monitoring_report()
    razorpay_res = demo_razorpay_redesign_scenario()
    
    return {
        "data_contract_testing": contract_res,
        "sla_monitoring_report": sla_res,
        "razorpay_redesign_case_study": razorpay_res
    }

def demo_pandera_contract_testing() -> Dict[str, Any]:
    """Data Contract Testing with Pandera Schema Validation as Code"""
    customer_schema = pa.DataFrameSchema({
        "customer_id": pa.Column(int, checks=pa.Check.gt(0)),
        "first_name": pa.Column(str, nullable=False),
        "email": pa.Column(str, checks=pa.Check.str_contains("@")),
        "total_spend": pa.Column(float, checks=pa.Check.ge(0.0))
    })
    
    df_valid = pd.DataFrame([
        {"customer_id": 1, "first_name": "Aarav", "email": "aarav@example.com", "total_spend": 1500.0},
        {"customer_id": 2, "first_name": "Diya", "email": "diya@example.com", "total_spend": 2400.5}
    ])
    
    try:
        validated_df = customer_schema.validate(df_valid)
        validation_passed = True
        error_msg = None
    except Exception as e:
        validation_passed = False
        error_msg = str(e)
        
    return {
        "contract_tool": "Pandera Schema Validation as Code",
        "validation_passed": validation_passed,
        "error_details": error_msg,
        "validated_rows": len(validated_df) if validation_passed else 0
    }

def demo_sla_monitoring_report() -> Dict[str, Any]:
    """SLA Monitoring & Pipeline KPI Audit Query"""
    q = """
        SELECT 
            pipeline_id,
            COUNT(run_id) as total_runs,
            SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_runs,
            SUM(records_extracted) as total_extracted,
            SUM(records_loaded) as total_loaded,
            SUM(records_rejected) as total_rejected,
            ROUND(100.0 * SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) / COUNT(run_id), 2) as success_rate_pct
        FROM pipeline_run_audit
        GROUP BY pipeline_id;
    """
    rows = query_db(q)
    return {
        "kpi_report": [dict(r) for r in rows] if rows else "No run audit records logged yet"
    }

def demo_razorpay_redesign_scenario() -> Dict[str, Any]:
    """Razorpay Payment Pipeline Before vs After Redesign Case Study"""
    before_state = {
        "architecture": "Monolithic cron script writing directly to Gold database",
        "error_handling": "Silent failure / dropped transactions",
        "data_quality": "Manual monthly queries",
        "recovery": "Manual database restore"
    }
    after_state = {
        "architecture": "Medallion (Bronze -> Silver -> Gold) with Watermark tracking",
        "error_handling": "Transient retry + Dead Letter Queue (DLQ) isolation",
        "data_quality": "Automated Pandera contract validation as code",
        "recovery": "Idempotent re-run with committed watermark resume"
    }
    return {
        "scenario": "Razorpay Payment Pipeline Production Redesign",
        "before_redesign": before_state,
        "after_redesign": after_state
    }
