import pytest
from src.database import init_db
from src.data_generator import generate_all_data
from src.week1.part1_etl_fundamentals import run_part1_demos
from src.week1.part2_storage_movement import run_part2_demos
from src.week2.part1_dimensional_modeling import run_part1_demos as run_w2p1
from src.week2.part2_scd_surrogate_keys import run_part2_demos as run_w2p2
from src.capstone.flipkart_analytics import run_capstone

def test_full_pipeline_end_to_end():
    init_db()
    generate_all_data()
    
    w1p1_res = run_part1_demos()
    assert w1p1_res["full_load"]["loaded"] > 0
    
    w1p2_res = run_part2_demos()
    assert w1p2_res["medallion_pipeline"]["silver_customers"] > 0
    
    w2p1_res = run_w2p1()
    assert w2p1_res["star_schema_loading"]["fact_order_items_loaded"] > 0
    
    w2p2_res = run_w2p2()
    assert w2p2_res["scd_type_2"]["total_versions"] == 2
    
    capstone_res = run_capstone("all")
    assert capstone_res["quality_and_pii"]["gold_layer_free_of_direct_pii"] is True
