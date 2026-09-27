# Week 3 Part 1: Production Pipeline Patterns, Change Data Capture (CDC) & Dead Letter Queue (DLQ) Routing

---

## 📌 Module Overview
This module covers production-grade pipeline load strategies (**Append-Only, Incremental Upsert/Merge, Full Swap**), explores Change Data Capture (CDC) mechanics with Debezium log-based streams, establishes error classification rules, and implements the **Dead Letter Queue (DLQ)** pattern for corrupt data isolation.

---

## 🔄 1. Production Pipeline Load Strategies

Enterprise pipelines select load execution patterns based on target idempotency, write throughput, and query SLA requirements.

```
                           PRODUCTION LOAD STRATEGIES
                                       |
         +-----------------------------+-----------------------------+
         |                             |                             |
         v                             v                             v
  +--------------+              +--------------+              +--------------+
  | APPEND-ONLY  |              | MERGE / UPSERT|             | FULL SWAP    |
  | (Log / Fact) |              | (Atomic Key) |              | (Atomic Rename)|
  +--------------+              +--------------+              +--------------+
  High-throughput               Updates existing,              Atomically swaps
  event insertion.              inserts new rows.              temp stage table.
```

### Strategy Comparison

| Strategy | Execution Mechanism | Pros | Cons | Ideal Scenario |
| :--- | :--- | :--- | :--- | :--- |
| **Append-Only** | `INSERT INTO target SELECT ...` | Maximum write speed; zero lock contention | Creates duplicates if re-run without partition overwrite | Immutable event logs, clickstream, Bronze tables |
| **Merge / Upsert** | `MERGE INTO target USING stage ON key ...` | Idempotent; handles updates and inserts in one statement | High I/O overhead on large target tables | Silver & Gold dimensional tables, order status updates |
| **Full Swap** | Create `target_tmp`, load, atomic swap `ALTER TABLE target_tmp RENAME TO target` | Instant zero-downtime table refresh | Requires 2x storage during execution | Daily pre-computed reporting summaries, small lookup tables |

#### SQLite / Portable Upsert Pattern Example:
```sql
INSERT INTO silver_orders (order_id, customer_id, total_amount, order_status, updated_at)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(order_id) DO UPDATE SET
    total_amount = excluded.total_amount,
    order_status = excluded.order_status,
    updated_at = excluded.updated_at;
```

---

## ⚡ 2. Change Data Capture (CDC) Deep Dive

Change Data Capture (CDC) streams row-level mutation events (`INSERT`, `UPDATE`, `DELETE`) from relational database transaction logs (MySQL Binlog, PostgreSQL WAL) directly into event streams (Apache Kafka).

```
+--------------------+      +--------------------+      +--------------------+      +--------------------+
| OLTP Database      | ---> | Debezium CDC       | ---> | Kafka Topic        | ---> | Stream Consumer    |
| (PostgreSQL WAL)   |      | Connector          |      | (json / avro)      |      | (Lakehouse MERGE)  |
+--------------------+      +--------------------+      +--------------------+      +--------------------+
```

### CDC Event Schema Structure
Each CDC record contains operation metadata (`op`) and before/after row snapshots:
```json
{
  "op": "u", 
  "ts_ms": 1774728000000,
  "before": { "order_id": 501, "status": "PENDING", "amount": 1200.0 },
  "after":  { "order_id": 501, "status": "DELIVERED", "amount": 1200.0 }
}
```
- `"op": "c"` $\rightarrow$ Create (`INSERT`)
- `"op": "u"` $\rightarrow$ Update (`UPDATE`)
- `"op": "d"` $\rightarrow$ Delete (`DELETE`)

---

## 🚨 3. Error Classification & The Dead Letter Queue (DLQ) Pattern

In production pipelines, **never silently discard invalid or corrupted rows**. Doing so leads to missing financial data and untraceable reconciliation discrepancies.

```
+------------------+      +-----------------------+      +------------------------+
| Raw Source Input | ---> | Data Quality Gate     | ---> | Silver Target Table    |
+------------------+      | (Validation Engine)   |      | (Valid Clean Rows)     |
                          +-----------------------+      +------------------------+
                                      |
                                      | (Corrupted / Invalid Rows)
                                      v
                          +-----------------------------------------------+
                          | DEAD LETTER QUEUE (DLQ / Quarantine)          |
                          | [payload, error_code, reason_code, run_id]    |
                          +-----------------------------------------------+
```

### Error Classification Hierarchy
1. **Transient Network Error**: (e.g., HTTP 503, API rate limit 429, temporary DB lock) $\rightarrow$ **Retry with Exponential Backoff**.
2. **Data Format / Quality Error**: (e.g., negative price, invalid email, corrupt JSON) $\rightarrow$ **Isolate to DLQ / Quarantine table and continue processing good rows**.
3. **Schema / Infrastructure Error**: (e.g., missing mandatory database column, corrupted disk) $\rightarrow$ **Halt Pipeline & Alert On-Call Engineer**.

### DLQ Quarantine Table Schema:
```sql
CREATE TABLE rejected_records (
    rejection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    source_table TEXT NOT NULL,
    raw_payload TEXT NOT NULL,           -- Original row as JSON
    error_code TEXT NOT NULL,            -- e.g., 'ERR_NEG_PRICE'
    error_message TEXT NOT NULL,         -- Human readable diagnostic
    rejected_at TEXT NOT NULL
);
```
