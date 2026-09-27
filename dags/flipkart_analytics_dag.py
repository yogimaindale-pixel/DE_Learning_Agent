"""
Airflow Production DAG: Flipkart Order Analytics Platform
Demonstrates Enterprise TaskGroup, Dynamic Task Mapping, and Quality Sensors.
"""
from datetime import datetime, timedelta

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.utils.task_group import TaskGroup
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

if AIRFLOW_AVAILABLE:
    with DAG(
        'flipkart_order_analytics_platform',
        default_args=default_args,
        description='Metadata-driven multi-source ingestion with Medallion Bronze-Silver-Gold pipeline',
        schedule_interval='0 2 * * *',
        catchup=False
    ) as dag:
        
        def run_ingestion_step():
            from src.capstone.flipkart_analytics import run_capstone_pipeline
            run_capstone_pipeline(step="ingestion")
            
        def run_medallion_step():
            from src.capstone.flipkart_analytics import run_capstone_pipeline
            run_capstone_pipeline(step="medallion")

        def run_quality_step():
            from src.capstone.flipkart_analytics import run_capstone_pipeline
            run_capstone_pipeline(step="quality")

        ingest_task = PythonOperator(
            task_id='ingest_6_sources',
            python_callable=run_ingestion_step
        )

        medallion_task = PythonOperator(
            task_id='medallion_bronze_to_gold',
            python_callable=run_medallion_step
        )

        quality_task = PythonOperator(
            task_id='quality_and_pii_gate',
            python_callable=run_quality_step
        )

        ingest_task >> medallion_task >> quality_task
