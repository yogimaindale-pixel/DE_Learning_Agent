# Week 1 Part 2: Storage Layers & Data Movement

## Objectives
- Master the Medallion Architecture: Raw (Bronze) -> Staging (Silver) -> Curated (Gold).
- Benchmark file formats: CSV, JSON, and Parquet columnar storage.
- Implement restartable watermark loading with `last_run_ts` tracking.
- Learn SaaS connector normalization (Salesforce, HubSpot, Workday, SAP).

## 1. Medallion Storage Layer Architecture

```
Raw / OLTP / APIs / Events
          │
          ▼
   [ BRONZE LAYER ]   --> Raw Ingestion (Append-Only, exact source schema)
          │
          ▼
   [ SILVER LAYER ]   --> Cleaned, Deduplicated, PII Masked, Validated Schema
          │
          ▼
   [ GOLD LAYER ]     --> Aggregated Star Schema & Business Metrics
```

### Bronze Layer
- Preserves raw source records with ingestion metadata (`ingested_at`, `input_file`).
- Serves as the immutable replay source.

### Silver Layer
- Cleans invalid strings, enforces data types, deduplicates records by primary key.
- Applies column-level PII masking (`email -> e***l@example.com`, `phone -> ******1234`) and SHA-256 hashing.

### Gold Layer
- Denormalized star schema (Facts & Dimensions) and aggregated summary tables optimized for business analytics.

---

## 2. File Format Comparison

- **CSV**: Text-based, human-readable, row-oriented. High storage footprint, slow column filter performance.
- **JSON**: Flexible schema support, hierarchical data representation. Ideal for semi-structured app clickstream and API responses.
- **Parquet**: Columnar format with dictionary encoding and Snappy compression. Fast projection queries and minimal I/O overhead.

---

## 3. Watermark Incremental Load Pattern
```sql
SELECT * FROM oltp_orders 
WHERE updated_at > :last_watermark 
ORDER BY updated_at ASC;
```
Watermark advances to `MAX(updated_at)` **only after** transaction commits to target Silver storage.
