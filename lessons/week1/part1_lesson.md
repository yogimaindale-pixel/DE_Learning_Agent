# Week 1 Part 1: Comprehensive Guide to ETL vs ELT, Ingestion Patterns & Source Systems

---

## 📌 Module Overview
This module covers the core foundation of modern enterprise Data Engineering: how raw data moves from source systems into storage and analytical warehouses. You will master the architectural trade-offs between **ETL (Extract, Transform, Load)** and **ELT (Extract, Load, Transform)**, explore the four core data ingestion patterns, connect to heterogeneous source systems, and master production integration for REST APIs with rate limits, pagination, and exponential backoff.

---

## 🏢 1. Real-World Architectural Trade-Offs: ETL vs ELT

### Scenario A: Regulated Banking Architecture (HDFC Bank — ETL Approach)
In traditional, heavily regulated financial institutions like **HDFC Bank**, enterprise data engineering prioritizes strict compliance, PII masking, data governance, and regulatory auditing before data ever reaches a central data warehouse.

```
+------------------+      +-----------------------+      +----------------------+      +------------------------+
| OLTP Core Banking| ---> | Isolated ETL Staging  | ---> | PII Tokenization     | ---> | Enterprise Data        |
| (Oracle / Finacle)      | (In-Flight Processing) |      | & Masking Gate       |      | Warehouse (EDW)        |
+------------------+      +-----------------------+      +----------------------+      +------------------------+
```

#### Why ETL for HDFC Bank?
1. **Security & Regulatory Compliance**: Banking regulations (RBI, PCI-DSS, DPDP Act) prohibit unencrypted PII (PAN card, Aadhaar number, credit card details) from sitting in raw data lakes without tokenization.
2. **Compute Cost Efficiency on Legacy EDW**: Enterprise data warehouses (e.g., Teradata, Exadata) charge premium rates for storage and compute. Cleaning and filtering invalid rows *before* loading saves storage and execution costs.
3. **Deterministic Quality Gates**: Invalid transactions or unverified ledger entries are halted in staging before contaminating downstream accounting reports.

---

### Scenario B: E-Commerce Marketplace Architecture (Meesho — ELT Approach)
In fast-growing e-commerce marketplaces like **Meesho**, millions of daily order events, seller clicks, and product catalog updates arrive concurrently from millions of mobile devices.

```
+------------------+      +-----------------------+      +----------------------+      +------------------------+
| Meesho App Events| ---> | Cloud Storage Lake    | ---> | Modern Lakehouse     | ---> | On-Demand Compute      |
| & Order Microservices   | (Raw S3 / Delta Lake) |      | (Bronze Layer)       |      | (Spark / Snowflake ELT) |
+------------------+      +-----------------------+      +----------------------+      +------------------------+
```

#### Why ELT for Meesho?
1. **Unstructured & Semi-Structured Data Velocity**: Raw JSON logs change schemas frequently. ELT dumps raw JSON directly into the cloud data lake without blocking ingestion.
2. **Elastic Cloud Compute**: Storage (Amazon S3 / Google Cloud Storage) is extremely cheap. Massive parallel transformations (dbt, Spark, Snowflake) run on-demand after ingestion.
3. **Flexibility for Multiple Analytical Use Cases**: Data scientists, product analysts, and BI engineers can query the original raw data with different business logic without re-ingesting.

---

### Summary Comparison Table: ETL vs ELT

| Metric / Dimension | Traditional ETL | Modern ELT |
| :--- | :--- | :--- |
| **Primary Sequence** | Extract -> Transform -> Load | Extract -> Load -> Transform |
| **Data Processing Location** | Dedicated ETL Engine (Informatica / SSIS / Spark) | Target Warehouse / Lakehouse (Snowflake / BigQuery / Databricks) |
| **Target Storage Payload** | Clean, transformed schema | Raw data payload + transformed layers |
| **Schema Flexibility** | Schema-on-Write (Rigid) | Schema-on-Read (Flexible) |
| **Primary Scenario** | HDFC Bank, Healthcare, PCI/PII strict systems | Meesho, Flipkart, Swiggy, SaaS analytics |
| **Cost Driver** | ETL processing servers + EDW storage | Cloud compute processing hours |

---

## 🔄 2. Ingestion Patterns Deep Dive

Enterprise pipelines employ four distinct ingestion patterns depending on data volume, update frequency, latency requirements, and source system capability.

```
                                  +---------------------------------------+
                                  | DATA INGESTION PATTERNS               |
                                  +---------------------------------------+
                                                      |
         +--------------------+-----------------------+--------------------+--------------------+
         |                    |                                            |                    |
         v                    v                                            v                    v
  +--------------+    +----------------+                            +-------------+      +--------------+
  |  FULL LOAD   |    | INCREMENTAL    |                            |  CDC        |      | STREAMING    |
  |  (Batch)     |    | (Watermarked)  |                            | (Log-based) |      | (Real-time)  |
  +--------------+    +----------------+                            +-------------+      +--------------+
```

### 1. Full Load Pattern
- **Definition**: Reads the entire dataset from the source system every run and completely overwrites or appends to the target table.
- **When to Use**: Small datasets (< 100,000 rows), reference lookups, static master dimensions (e.g., store locations, postal code mappings).
- **Pros**: Simple to write; no complex change tracking required.
- **Cons**: High I/O overhead; unscalable for growing transaction tables; risk of table lock during replacement.

### 2. Incremental Load Pattern (Watermarking)
- **Definition**: Reads only records created or modified since the last successful pipeline execution timestamp (`watermark_ts`).
- **When to Use**: Large transaction tables (orders, line items, user activity logs) that contain an `updated_at` or `created_at` timestamp index.
- **Formula**:
  $$\text{Query} = \text{"SELECT * FROM orders WHERE updated\_at > '\} + \text{last\_watermark} + \text{"'"}$$
- **Pros**: Low network I/O; scalable to billions of rows; cost-effective.
- **Cons**: Misses hard deletes unless soft-delete flags (`is_deleted = 1`) are recorded in the source table.

### 3. Change Data Capture (CDC)
- **Definition**: Reads transaction logs (e.g., MySQL Binlog, PostgreSQL WAL) directly from the database engine to capture every `INSERT`, `UPDATE`, and `DELETE` event in real-time.
- **Technology**: Apache Kafka, Debezium, AWS Database Migration Service (DMS).
- **Pros**: Zero impact on source database performance; captures deleted rows and intermediate state transitions.
- **Cons**: Requires database administrator (DBA) permissions and complex log-parsing infrastructure.

### 4. Streaming Ingestion Pattern
- **Definition**: Processes continuous event streams record-by-record or in sub-second micro-batches.
- **Technology**: Apache Kafka, AWS Kinesis, Apache Flink, Spark Streaming.
- **Real-World Scenario**: **Swiggy / Zepto / Hotstar**: Continuous delivery rider GPS updates, payment auth events, or video buffer logs.
- **Pros**: Sub-second latency for real-time dashboards and fraud detection.
- **Cons**: High infrastructure operational complexity; eventual consistency challenges.

---

## 🌐 3. Connecting to Heterogeneous Source Systems

Enterprise pipelines consume data from four primary source paradigms:

1. **Relational OLTP Databases**: PostgreSQL, MySQL, SQLite, Oracle via JDBC/ODBC and SQL parameterization.
2. **Flat File Systems**: CSV, TSV, Parquet, JSON files delivered to S3/GCS or SFTP drop zones.
3. **Event Streams**: Kafka topics, AWS Kinesis, RabbitMQ emitting JSON or Avro messages.
4. **SaaS & REST APIs**: Stripe, Razorpay, Salesforce, HubSpot returning JSON payloads.

---

## ⚡ 4. Production REST API Integration: Pagination, Rate Limits & Backoff

When consuming SaaS APIs (e.g., **Razorpay Payment API**), data engineers must handle three network challenges:

```
[ETL Pipeline] ---> Request Page 1 ---> [Razorpay API]
[ETL Pipeline] <--- Response 200 (Has Next Page) <--- [Razorpay API]
[ETL Pipeline] ---> Request Page 2 (Too Fast!) ---> [Razorpay API]
[ETL Pipeline] <--- Response 429 Too Many Requests <--- [Razorpay API]
[ETL Pipeline] -- Wait Exponential Backoff (2s, 4s, 8s) -- Retry Page 2 ---> [Razorpay API]
```

### A. Pagination Strategies
- **Offset/Limit**: Requesting `?offset=0&limit=100`, then `?offset=100&limit=100`. (Performance degrades at deep offsets).
- **Cursor-Based Pagination**: Requesting `?cursor=opaque_token_xyz`. The API returns `next_cursor`. (Fast, consistent, recommended for large scale).

### B. Rate Limit Handling (HTTP 429) & Exponential Backoff
When an API returns `HTTP 429 Too Many Requests`, pipelines must pause before retrying.
Using **Exponential Backoff with Full Jitter**:

$$t_{\text{wait}} = \min\left(t_{\text{max}}, t_{\text{base}} \times 2^{\text{attempt}}\right) + \text{random}(0, \text{jitter})$$

#### Python Implementation Example:
```python
import time
import random
import requests

def fetch_api_with_backoff(url, max_retries=5):
    base_delay = 1.0
    max_delay = 32.0
    
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                sleep_time = float(retry_after)
            else:
                sleep_time = min(max_delay, base_delay * (2 ** attempt)) + random.uniform(0, 0.5)
            print(f"[HTTP 429] Rate limited. Retrying in {sleep_time:.2f}s...")
            time.sleep(sleep_time)
        else:
            response.raise_for_status()
            
    raise Exception("Max retries exceeded for API endpoint.")
```

---

## 🛠️ Summary & Key Takeaways
1. Choose **ETL** when security, PII protection, and strict governance before warehouse load are mandatory (e.g., HDFC Bank).
2. Choose **ELT** when speed, unstructured payloads, and cloud lakehouse elasticity are paramount (e.g., Meesho).
3. Use **Incremental Watermarks** for transaction tables and **CDC/Streaming** for sub-minute real-time delivery (e.g., Swiggy).
4. Always build **Exponential Backoff** and **Watermark Checkpointing** into SaaS API connectors.
