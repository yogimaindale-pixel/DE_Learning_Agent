import sqlite3
from typing import Dict, Any, List
from src.config import get_pipelines_config
from src.database import get_connection, query_db, execute_query
from src.logging_utils import logger, generate_run_id

def run_part1_demos() -> Dict[str, Any]:
    logger.info("Running Week 4 Part 1 Orchestration & Metadata Engine Demos...")
    
    metadata_res = demo_metadata_driven_generic_engine()
    airflow_concepts = demo_airflow_patterns_simulation()
    
    return {
        "metadata_engine_execution": metadata_res,
        "airflow_orchestration_patterns": airflow_concepts
    }

def demo_metadata_driven_generic_engine() -> Dict[str, Any]:
    """Metadata-Driven Ingestion Engine: Reads pipeline_control and runs N sources generically"""
    run_id = generate_run_id()
    pipelines = query_db("SELECT pipeline_id, pipeline_name, source_type, target_table, last_watermark FROM pipeline_control WHERE is_active = 1;")
    
    results = []
    conn = get_connection()
    cur = conn.cursor()
    
    for pipe in pipelines:
        pid = pipe["pipeline_id"]
        stype = pipe["source_type"]
        target = pipe["target_table"]
        
        # Generic Execution Logic based on metadata
        extracted = 100
        loaded = 100
        rejected = 0
        
        cur.execute("""
            INSERT INTO pipeline_run_audit (run_id, pipeline_id, status, records_extracted, records_loaded, records_rejected, start_time, end_time)
            VALUES (?, ?, 'SUCCESS', ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """, (run_id, pid, extracted, loaded, rejected))
        
        results.append({
            "pipeline_id": pid,
            "name": pipe["pipeline_name"],
            "target": target,
            "status": "SUCCESS"
        })
        
    conn.commit()
    conn.close()
    
    return {
        "engine_type": "Generic Metadata-Driven Pipeline Engine",
        "pipelines_processed": len(results),
        "pipeline_details": results
    }

def demo_airflow_patterns_simulation() -> Dict[str, Any]:
    """Simulates Airflow Dynamic Task Mapping, TaskGroups, Sensors & Fan-Out/Fan-In"""
    return {
        "TaskGroup": "Grouping Bronze Ingestion tasks into parallel execution blocks",
        "DynamicTaskMapping": "Expanding ingestion tasks dynamically based on source list",
        "ExternalTaskSensor": "Waiting for upstream Core OLTP DAG completion before Gold Refresh",
        "FanOut_FanIn": "Fan-out: Ingest 6 sources in parallel -> Fan-in: Quality Gate check before publishing Gold summary"
    }
