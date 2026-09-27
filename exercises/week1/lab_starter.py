# Week 1 Lab Exercise: Incremental Load with Watermark

# TODO: Fill in the missing extraction SQL query to fetch records newer than last_run_ts

def extract_incremental_orders(conn, last_run_ts: str):
    # TODO: Modify the query below to filter by updated_at > last_run_ts
    query = """
        SELECT * FROM oltp_orders
        -- WHERE updated_at > ?
        ORDER BY updated_at ASC;
    """
    # cursor = conn.cursor()
    # return cursor.execute(query, (last_run_ts,)).fetchall()
    pass
