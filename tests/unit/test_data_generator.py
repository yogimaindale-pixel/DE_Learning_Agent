import pytest
from src.database import init_db, query_db
from src.data_generator import generate_all_data

def test_db_initialization_and_data_generation():
    init_db()
    generate_all_data()
    
    customers = query_db("SELECT COUNT(*) as cnt FROM oltp_customers;")
    orders = query_db("SELECT COUNT(*) as cnt FROM oltp_orders;")
    products = query_db("SELECT COUNT(*) as cnt FROM oltp_products;")
    
    assert customers[0]["cnt"] == 100
    assert orders[0]["cnt"] >= 200
    assert products[0]["cnt"] == 50
