# Week 1 Part 1: ETL Fundamentals & Data Movement

## Objectives
- Understand ETL vs ELT trade-offs using real-world business scenarios: HDFC Bank (ETL) vs Meesho (ELT).
- Master ingestion patterns: Full Load, Incremental Load, CDC, and Streaming.
- Connect to OLTP databases, REST APIs, flat files, and Kafka-like streams.
- Handle REST API pagination, HTTP 429 rate limits, authentication, and exponential backoff retries.

## 1. ETL vs ELT Trade-Offs

### HDFC Bank (Regulated Banking - ETL)
In regulated financial systems like HDFC Bank, customer data contains sensitive Personal Identifiable Information (PII) and Payment Card Industry (PCI) records. Before data touches the Enterprise Data Warehouse (EDW):
- **Security & Privacy**: PII fields must be masked or tokenized in-flight.
- **Latency vs Governance**: Transformations must run in secure, isolated ETL staging pipelines to guarantee compliance before persistence.

### Meesho (E-Commerce Marketplace - ELT)
In fast-growing e-commerce marketplaces like Meesho:
- **Scalability & Latency**: Raw JSON payloads and order logs are rapidly loaded into cheap cloud storage (S3/GCS) and Delta/Iceberg tables.
- **Compute Elasticity**: Transformations run on-demand using distributed compute engines (Spark/Trino/Snowflake) after data is safely ingested into the lakehouse.

---

## 2. Ingestion Patterns

| Ingestion Pattern | Volume | Latency | Key Use Case |
| :--- | :--- | :--- | :--- |
| **Full Load** | Small (< 100K) | Daily/Weekly | Master tables, static dimensions |
| **Incremental Load** | Medium/Large | Hourly/Daily | Orders with `updated_at` watermark |
| **CDC (Change Data Capture)** | Large / High Ops | Sub-minute | OLTP DB replication (Debezium/Kafka) |
| **Streaming** | High frequency | Sub-second | Clickstream, Swiggy/Zepto live tracking |

---

## 3. REST API Pagination & Rate Limits (Stripe/Razorpay API)
When integrating SaaS and payment APIs:
1. **Pagination**: Iterate through pages using offset/limit or cursor tokens (`next_page_url`).
2. **Rate Limits (HTTP 429)**: Respect `Retry-After` headers. Use **Exponential Backoff with Jitter** to delay retries: `delay = min(max_delay, base * (2 ^ attempt) + jitter)`.
3. **Checkpointing**: Store the last successfully fetched cursor/page in `pipeline_control` to resume seamlessly after unexpected network interruptions.
