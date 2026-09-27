# Week 1 Lab Exercise Solution: Incremental Load with Watermark

def extract_incremental_orders(conn, last_run_ts: str):
    query = """
        SELECT order_id, customer_id, store_id, order_status, total_amount, created_at, updated_at
        FROM oltp_orders
        WHERE updated_at > ?
        ORDER BY updated_at ASC;
    """
    cursor = conn.cursor()
    return cursor.execute(query, (last_run_ts,)).fetchall()
