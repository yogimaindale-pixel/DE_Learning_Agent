import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.database import get_connection, query_db, execute_query
from src.logging_utils import logger

def run_part1_demos() -> Dict[str, Any]:
    logger.info("Running Week 2 Part 1 Dimensional Modeling & Window Queries Demos...")
    
    _populate_date_dimension()
    star_result = build_star_schema()
    window_results = run_window_function_queries()
    join_antipattern_result = diagnose_join_fanout_antipattern()
    
    return {
        "star_schema_loading": star_result,
        "window_queries": window_results,
        "join_antipattern_diagnosis": join_antipattern_result
    }

def _populate_date_dimension() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM dim_date;")
    if cursor.fetchone()["cnt"] > 0:
        conn.close()
        return
        
    start_date = datetime(2024, 1, 1)
    days = 366
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    month_names = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    for i in range(days):
        dt = start_date + timedelta(days=i)
        date_key = int(dt.strftime("%Y%m%d"))
        full_date = dt.strftime("%Y-%m-%d")
        dow = dt.weekday()
        day_name = day_names[dow]
        month = dt.month
        month_name = month_names[month]
        quarter = (month - 1) // 3 + 1
        year = dt.year
        is_weekend = 1 if dow in [5, 6] else 0
        
        cursor.execute("""
            INSERT INTO dim_date (date_key, full_date, day_of_week, day_name, month, month_name, quarter, year, is_weekend)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (date_key, full_date, day_name, day_name, month, month_name, quarter, year, is_weekend))
        
    conn.commit()
    conn.close()

def build_star_schema() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Populate dim_store
    cursor.execute("""
        INSERT INTO dim_store (store_id, store_name, city, state)
        SELECT store_id, store_name, city, state FROM oltp_stores
        WHERE store_id NOT IN (SELECT store_id FROM dim_store);
    """)
    
    # 2. Populate dim_product (Type 1 base)
    cursor.execute("""
        INSERT INTO dim_product (product_id, product_name, category, current_price, effective_date)
        SELECT product_id, product_name, category, price, '2024-01-01'
        FROM oltp_products
        WHERE product_id NOT IN (SELECT product_id FROM dim_product);
    """)
    
    # 3. Populate fact_order_item
    cursor.execute("""
        INSERT INTO fact_order_item (order_id, customer_sk, product_sk, store_sk, date_key, quantity, unit_price, total_price, net_amount)
        SELECT 
            i.order_id,
            COALESCE(c.customer_sk, -1) as customer_sk,
            COALESCE(p.product_sk, -1) as product_sk,
            COALESCE(s.store_sk, -1) as store_sk,
            CAST(strftime('%Y%m%d', o.created_at) AS INTEGER) as date_key,
            i.quantity,
            i.unit_price,
            (i.quantity * i.unit_price) as total_price,
            (i.quantity * i.unit_price) as net_amount
        FROM oltp_order_items i
        JOIN oltp_orders o ON i.order_id = o.order_id
        LEFT JOIN dim_customer c ON o.customer_id = c.customer_id AND c.is_current = 1
        LEFT JOIN dim_product p ON i.product_id = p.product_id AND p.is_current = 1
        LEFT JOIN dim_store s ON o.store_id = s.store_id
        WHERE i.order_id NOT IN (SELECT order_id FROM fact_order_item);
    """)
    
    conn.commit()
    
    fact_count = cursor.execute("SELECT COUNT(*) as cnt FROM fact_order_item;").fetchone()["cnt"]
    dim_cust_count = cursor.execute("SELECT COUNT(*) as cnt FROM dim_customer;").fetchone()["cnt"]
    dim_prod_count = cursor.execute("SELECT COUNT(*) as cnt FROM dim_product;").fetchone()["cnt"]
    conn.close()
    
    return {
        "fact_order_items_loaded": fact_count,
        "dim_customers_count": dim_cust_count,
        "dim_products_count": dim_prod_count
    }

def run_window_function_queries() -> Dict[str, Any]:
    # Query 1: Top 3 products per category by sales volume (ROW_NUMBER & RANK)
    q1 = """
        WITH prod_sales AS (
            SELECT 
                p.category,
                p.product_name,
                SUM(f.quantity) as total_qty,
                ROW_NUMBER() OVER(PARTITION BY p.category ORDER BY SUM(f.quantity) DESC) as rnk
            FROM fact_order_item f
            JOIN dim_product p ON f.product_sk = p.product_sk
            GROUP BY p.category, p.product_name
        )
        SELECT category, product_name, total_qty, rnk
        FROM prod_sales
        WHERE rnk <= 3;
    """
    res1 = query_db(q1)
    
    # Query 2: Customer monthly order lag & lead (LAG / LEAD)
    q2 = """
        WITH monthly_orders AS (
            SELECT 
                customer_sk,
                date_key / 100 as order_month,
                COUNT(DISTINCT order_id) as month_orders,
                LAG(COUNT(DISTINCT order_id), 1) OVER(PARTITION BY customer_sk ORDER BY date_key / 100) as prev_month_orders,
                LEAD(COUNT(DISTINCT order_id), 1) OVER(PARTITION BY customer_sk ORDER BY date_key / 100) as next_month_orders
            FROM fact_order_item
            WHERE customer_sk != -1
            GROUP BY customer_sk, date_key / 100
        )
        SELECT * FROM monthly_orders LIMIT 5;
    """
    res2 = query_db(q2)
    
    # Query 3: Running revenue cumulative sum (SUM OVER)
    q3 = """
        SELECT 
            date_key,
            SUM(net_amount) as daily_net,
            SUM(SUM(net_amount)) OVER(ORDER BY date_key ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as running_total
        FROM fact_order_item
        GROUP BY date_key
        ORDER BY date_key
        LIMIT 5;
    """
    res3 = query_db(q3)
    
    return {
        "top_products_per_category_sample": [dict(r) for r in res1[:3]],
        "customer_lag_lead_sample": [dict(r) for r in res2],
        "running_revenue_sample": [dict(r) for r in res3]
    }

def diagnose_join_fanout_antipattern() -> Dict[str, Any]:
    """Diagnoses double counting due to 1-to-N join fan-out in Puma/Nykaa scenario"""
    bad_query = """
        SELECT 
            o.order_id,
            o.total_amount as order_table_total,
            SUM(i.unit_price * i.quantity) as items_sum
        FROM oltp_orders o
        JOIN oltp_order_items i ON o.order_id = i.order_id
        GROUP BY o.order_id, o.total_amount
        HAVING COUNT(i.item_id) > 1;
    """
    rows = query_db(bad_query)
    
    explanation = (
        "Anti-pattern Diagnosis: Joining 1-to-N tables before aggregating without explicit grain "
        "causes line items to duplicate header totals if SUM(o.total_amount) is performed. "
        "Solution: Always aggregate at the line-item grain or pre-aggregate before joining."
    )
    
    return {
        "fanout_orders_diagnosed": len(rows),
        "explanation": explanation
    }
