import json
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path
from src.config import DATA_DIR, DB_PATH
from src.database import get_connection
from src.logging_utils import logger

SEED = 42

def generate_all_data() -> None:
    logger.info("Generating synthetic reproducible data (seed=42)...")
    random.seed(SEED)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for sub in ["raw", "staging", "curated", "serving", "quarantine"]:
        (DATA_DIR / sub).mkdir(parents=True, exist_ok=True)
        
    conn = get_connection()
    _populate_oltp_tables(conn)
    conn.close()
    
    _generate_csv_files()
    _generate_json_files()
    _generate_kafka_ndjson_stream()
    _generate_mock_api_feed()
    logger.info("Synthetic data generation complete.")

def _populate_oltp_tables(conn) -> None:
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM oltp_order_items;")
    cursor.execute("DELETE FROM oltp_orders;")
    cursor.execute("DELETE FROM oltp_customers;")
    cursor.execute("DELETE FROM oltp_products;")
    cursor.execute("DELETE FROM oltp_stores;")
    
    # 1. Customers
    cities = ["Mumbai", "Bengaluru", "Delhi", "Hyderabad", "Pune", "Chennai", "Kolkata", "Ahmedabad"]
    states = ["Maharashtra", "Karnataka", "Delhi", "Telangana", "Maharashtra", "Tamil Nadu", "West Bengal", "Gujarat"]
    
    base_time = datetime(2024, 1, 1, 10, 0, 0)
    for i in range(1, 101):
        city_idx = random.randint(0, len(cities) - 1)
        created_at = (base_time + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d %H:%M:%S")
        updated_at = created_at
        
        email = f"user_{i}@example.com" if i != 15 else "invalid_email_format"
        first_name = f"CustFirst{i}"
        last_name = f"CustLast{i}"
        phone = f"+919876543{i:03d}"
        
        cursor.execute("""
            INSERT INTO oltp_customers (customer_id, first_name, last_name, email, phone, city, state, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (i, first_name, last_name, email, phone, cities[city_idx], states[city_idx], created_at, updated_at))
        
    # 2. Stores
    stores = [
        (1, "Indiranagar Store", "Bengaluru", "Karnataka"),
        (2, "Koramangala Hub", "Bengaluru", "Karnataka"),
        (3, "Bandra Flagship", "Mumbai", "Maharashtra"),
        (4, "CP Connaught Place", "Delhi", "Delhi"),
        (5, "Gachibowli Center", "Hyderabad", "Telangana")
    ]
    for store in stores:
        cursor.execute("INSERT INTO oltp_stores VALUES (?, ?, ?, ?);", store)
        
    # 3. Products
    categories = ["Eyewear", "Electronics", "Fashion", "Groceries", "Personal Care"]
    for i in range(1, 51):
        p_name = f"Product_{i}"
        cat = categories[i % len(categories)]
        price = round(random.uniform(100.0, 5000.0), 2)
        created_at = "2024-01-01 00:00:00"
        cursor.execute("""
            INSERT INTO oltp_products (product_id, product_name, category, price, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (i, p_name, cat, price, created_at, created_at))
        
    # 4. Orders & Items
    statuses = ["DELIVERED", "PROCESSING", "CANCELLED", "PENDING"]
    
    item_id_seq = 1
    for order_id in range(1, 201):
        cust_id = random.randint(1, 100)
        store_id = random.randint(1, 5)
        status = random.choice(statuses)
        order_dt = base_time + timedelta(days=random.randint(1, 200), hours=random.randint(0, 12))
        created_at = order_dt.strftime("%Y-%m-%d %H:%M:%S")
        updated_at = (order_dt + timedelta(hours=random.randint(1, 48))).strftime("%Y-%m-%d %H:%M:%S")
        
        num_items = random.randint(1, 4)
        order_total = 0.0
        
        # Insert parent order first
        cursor.execute("""
            INSERT INTO oltp_orders (order_id, customer_id, store_id, order_status, total_amount, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (order_id, cust_id, store_id, status, 0.0, created_at, updated_at))
        
        for _ in range(num_items):
            prod_id = random.randint(1, 50)
            qty = random.randint(1, 3)
            if order_id == 75:
                qty = -2 # Anomaly
            unit_price = round(random.uniform(200.0, 1500.0), 2)
            item_total = qty * unit_price
            order_total += max(0.0, item_total)
            
            cursor.execute("""
                INSERT INTO oltp_order_items (item_id, order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?, ?);
            """, (item_id_seq, order_id, prod_id, qty, unit_price))
            item_id_seq += 1
            
        # Update total amount
        cursor.execute("""
            UPDATE oltp_orders SET total_amount = ? WHERE order_id = ?;
        """, (round(order_total, 2), order_id))
        
    conn.commit()

def _generate_csv_files() -> None:
    raw_dir = DATA_DIR / "raw"
    
    with open(raw_dir / "products.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "product_name", "category", "price", "updated_at"])
        for i in range(1, 51):
            writer.writerow([i, f"Product_CSV_{i}", "Eyewear" if i % 2 == 0 else "Accessories", round(150 + i * 12.5, 2), "2024-05-01 08:00:00"])
            
    with open(raw_dir / "customers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["customer_id", "first_name", "last_name", "email", "phone", "city", "state", "updated_at"])
        for i in range(1, 101):
            email = f"csv_cust_{i}@example.com" if i != 22 else "bad_email_at_domain"
            writer.writerow([i, f"CSV_First{i}", f"CSV_Last{i}", email, f"+919123456{i:03d}", "Bengaluru", "Karnataka", "2024-05-01 08:00:00"])

def _generate_json_files() -> None:
    raw_dir = DATA_DIR / "raw"
    
    events = []
    base_time = datetime(2024, 6, 1, 10, 0, 0)
    for i in range(1, 101):
        event = {
            "event_id": f"evt_{i:04d}",
            "user_id": random.randint(1, 100),
            "event_type": random.choice(["page_view", "add_to_cart", "checkout", "search"]),
            "timestamp": (base_time + timedelta(minutes=i*5)).isoformat(),
            "device": random.choice(["iOS", "Android", "Web"])
        }
        if i == 50:
            event["new_unannounced_field"] = "schema_drift_detected"
            event["user_id"] = "STRING_INSTEAD_OF_INT"
        events.append(event)
        
    with open(raw_dir / "app_events.json", "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)
        
    saas_data = []
    for i in range(1, 21):
        saas_data.append({
            "employee_id": f"EMP-{i:03d}",
            "full_name": f"Employee {i}",
            "department": random.choice(["Engineering", "Data", "Product", "Sales"]),
            "ssn": f"999-00-{i:04d}",
            "personal_email": f"emp_{i}@private.com",
            "hire_date": "2023-01-15"
        })
    with open(raw_dir / "saas_exports.json", "w", encoding="utf-8") as f:
        json.dump(saas_data, f, indent=2)

def _generate_kafka_ndjson_stream() -> None:
    raw_dir = DATA_DIR / "raw"
    base_time = datetime(2024, 6, 1, 12, 0, 0)
    
    with open(raw_dir / "delivery_stream.ndjson", "w", encoding="utf-8") as f:
        for i in range(1, 51):
            msg = {
                "delivery_id": i,
                "order_id": i,
                "status": random.choice(["ASSIGNED", "PICKED", "DELIVERED"]),
                "delivery_partner_id": random.randint(101, 110),
                "delivery_address": f"Flat {i}, Residency Road, Bengaluru",
                "timestamp": (base_time + timedelta(minutes=i*3)).strftime("%Y-%m-%d %H:%M:%S")
            }
            f.write(json.dumps(msg) + "\n")

def _generate_mock_api_feed() -> None:
    raw_dir = DATA_DIR / "raw"
    payments = []
    base_time = datetime(2024, 6, 1, 10, 0, 0)
    
    for i in range(1, 101):
        payments.append({
            "payment_id": f"pay_{i:04d}",
            "order_id": i,
            "payment_method": random.choice(["UPI", "CREDIT_CARD", "NET_BANKING", "WALLET"]),
            "payment_status": random.choice(["SUCCESS", "SUCCESS", "SUCCESS", "FAILED"]),
            "amount": round(random.uniform(200.0, 3000.0), 2),
            "card_last4": f"{random.randint(1000, 9999)}",
            "created_at": (base_time + timedelta(minutes=i*10)).strftime("%Y-%m-%d %H:%M:%S")
        })
        
    feed = {
        "page": 1,
        "total_pages": 2,
        "data": payments[:50],
        "next_page_url": "/api/v1/payments?page=2"
    }
    
    with open(raw_dir / "mock_payments_api_page1.json", "w", encoding="utf-8") as f:
        json.dump(feed, f, indent=2)
        
    feed_page2 = {
        "page": 2,
        "total_pages": 2,
        "data": payments[50:],
        "next_page_url": None
    }
    with open(raw_dir / "mock_payments_api_page2.json", "w", encoding="utf-8") as f:
        json.dump(feed_page2, f, indent=2)
