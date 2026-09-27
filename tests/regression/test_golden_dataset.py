import pytest
from src.database import init_db, query_db
from src.data_generator import generate_all_data
from src.week1.part1_etl_fundamentals import run_part1_demos
from src.week1.part2_storage_movement import run_part2_demos

def test_golden_dataset_regression():
    init_db()
    generate_all_data()
    run_part1_demos()
    run_part2_demos()
    
    # Golden Baseline Expectations for Seed 42:
    # 100 raw customers generated, customer 15 has invalid email so 1 quarantined -> 99 valid silver customers
    silver_cust_count = query_db("SELECT COUNT(*) as cnt FROM silver_customers;")[0]["cnt"]
    quarantine_count = query_db("SELECT COUNT(*) as cnt FROM rejected_records;")[0]["cnt"]
    
    assert silver_cust_count == 99
    assert quarantine_count >= 1
