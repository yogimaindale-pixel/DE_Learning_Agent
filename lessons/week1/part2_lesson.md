# Week 1 Part 2: Storage Layers, Medallion Architecture, File Formats & Watermarking

---

## 📌 Module Overview
This module covers how modern data architectures organize data into distinct storage layers (Raw, Staging, Curated, Serving / Bronze, Silver, Gold), compare storage file formats (Parquet, CSV, JSON), implement restartable watermark incremental state tracking, and process event-driven stream messages and SaaS exports.

---

## 🏛️ 1. Lakehouse Storage Architecture: The Medallion Paradigm

The **Medallion Architecture** standardizes data structures into three refined layers to ensure data quality, traceability, and high query performance:

```
+-------------------+      +-----------------------+      +-----------------------+
| BRONZE LAYER      | ---> | SILVER LAYER          | ---> | GOLD LAYER            |
| Raw Ingestion     |      | Cleansed & Validated  |      | Aggregated & Curated  |
| (Append-Only)     |      | (Conformed / PII Mask)|      | (Star Schema / KPIs)  |
+-------------------+      +-----------------------+      +-----------------------+
  Exact source copy          Type casting, dedupe,          Executive dashboards,
  with ingestion_ts          quarantine bad rows            daily business metrics
```

### Layer-by-Layer Breakdown

#### A. Bronze Layer (Raw Storage Zone)
- **Purpose**: Captures raw source data *as-is* without schema enforcement or data modification.
- **Characteristics**: Immutable, append-only, stores raw JSON/CSV payloads along with technical metadata: `_ingested_at`, `_source_file`, `_pipeline_id`.
- **Scenario**: **Swiggy Rider Tracking**: Raw JSON telemetry packets dumped directly into Bronze.

#### B. Silver Layer (Cleansed / Conformed Zone)
- **Purpose**: Cleanses, standardizes, type-casts, dedupes, and validates Bronze data.
- **Characteristics**: Enforces schema validation, handles missing values, masks PII fields (e.g., hashing phone numbers), and routes invalid rows to Quarantine tables.
- **Scenario**: **Puma India E-Commerce**: Silver customer table with standardized phone numbers (`+91`), verified postal codes, and unified lowercase email addresses.

#### C. Gold Layer (Curated / Serving Zone)
- **Purpose**: Business-level aggregations, star-schema fact and dimension tables, and analytical views optimized for BI tools (Tableau, PowerBI) and executive reporting.
- **Characteristics**: Pre-aggregated, highly performant, indexed, and sanitized (contains no direct PII).
- **Scenario**: **BigBasket / Flipkart**: Daily sales metrics by store location, customer RFM tiers, and product category revenue summaries.

---

## 📁 2. File Format Deep Dive: Parquet vs CSV vs JSON

Choosing the correct file format directly impacts pipeline throughput, network transfer costs, and analytical query speeds.

```
                          FILE FORMAT COMPARISON
                          
   CSV / JSON (Row-Oriented)               PARQUET (Columnar)
   +-----+--------+-------+                 +-------------------------+
   | ID  | Name   | Spend |                 | IDs:   [1, 2, 3]        |
   +-----+--------+-------+                 | Names: ['A', 'B', 'C']  |
   | 1   | Alice  | 100   |                 | Spend: [100, 200, 150]  |
   | 2   | Bob    | 200   |                 +-------------------------+
   +-----+--------+-------+                 Reads ONLY required col!
   Scans entire file for spend!
```

### Comparative Analysis Matrix

| Feature | CSV | JSON / NDJSON | Parquet |
| :--- | :--- | :--- | :--- |
| **Structure** | Plain Text (Row) | Semi-Structured (Row) | Binary Columnar |
| **Schema Storage** | None (Inferred) | Embedded in each row | Embedded metadata footer |
| **Compression** | Poor (gzip external) | Poor (gzip external) | High (Snappy / ZSTD built-in) |
| **Query Speed (Aggregations)**| Slow (Full I/O scan) | Slow (Parsing cost) | **Fast** (Column pruning + predicate pushdown) |
| **Nested Data Support** | No | Excellent | **Yes** (Repetition / Definition levels) |
| **Primary Use Case** | Manual exports, SFTP drops | API payloads, Kafka streams | **Data Lakes, Silver & Gold lakehouse layers** |

---

## ⏱️ 3. The Watermark Pattern for Restartable Incremental Loads

To guarantee that pipeline re-executions process only new data without dropping rows or creating duplicate records, enterprise pipelines maintain a **Control Watermark Table** (`pipeline_control`).

```
+-----------------------------------------------------------------------------------+
| CONTROL TABLE: pipeline_control                                                   |
+-------------------+--------------------+----------------------+-------------------+
| pipeline_id       | target_table       | last_processed_ts    | last_run_status   |
+-------------------+--------------------+----------------------+-------------------+
| p002              | bronze_orders      | 2026-09-27 18:00:00  | SUCCESS           |
+-------------------+--------------------+----------------------+-------------------+
```

### Watermark Execution Flow
1. **Fetch Watermark**: Read `last_processed_ts` for pipeline `p002` from `pipeline_control`.
2. **Extract Delta**: Query source where `updated_at > last_processed_ts AND updated_at <= current_execution_ts`.
3. **Transform & Load**: Process records into target table within a single transaction.
4. **Advance Watermark**: Update `last_processed_ts = current_execution_ts` **only after target transaction commits**.

```python
def run_incremental_watermark_pipeline(conn, pipeline_id, source_table, target_table):
    cur = conn.cursor()
    
    # 1. Read last watermark
    cur.execute("SELECT last_processed_ts FROM pipeline_control WHERE pipeline_id = ?;", (pipeline_id,))
    row = cur.fetchone()
    last_ts = row["last_processed_ts"] if row else "1900-01-01 00:00:00"
    
    current_run_ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    # 2. Query delta
    delta_rows = cur.execute(f"""
        SELECT * FROM {source_table} 
        WHERE updated_at > ? AND updated_at <= ?;
    """, (last_ts, current_run_ts)).fetchall()
    
    # 3. Insert into target inside transaction
    if delta_rows:
        cur.executemany(f"INSERT INTO {target_table} VALUES (?, ?, ...);", delta_rows)
        
        # 4. Advance watermark ONLY on success
        cur.execute("""
            UPDATE pipeline_control 
            SET last_processed_ts = ?, last_run_status = 'SUCCESS' 
            WHERE pipeline_id = ?;
        """, (current_run_ts, pipeline_id))
        conn.commit()
```

---

## 📡 4. Real-Time Streaming & SaaS Export Integration

### Real-Time Event Streams (Swiggy, Hotstar, Zepto)
- Real-time event streams (e.g., Kafka topics, Kinesis streams) deliver newline-delimited JSON (`NDJSON`).
- Pipelines process records in **micro-batches** (e.g., every 10 seconds or 1,000 records).
- **Handling Late Events**: Events arriving out-of-order due to network lag are re-ordered in Silver layer using `event_timestamp` rather than ingestion time.

### SaaS Connector Exports (Salesforce, Workday, SAP)
- Enterprise SaaS tools deliver periodic bulk exports (JSON/CSV) via cloud storage buckets or webhooks.
- **Canonical Normalization**: Raw nested JSON schemas from different vendor platforms (e.g., Workday employee structure vs SAP employee structure) are mapped into a unified **Canonical Employee Model** in the Silver layer.
