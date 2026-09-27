# Week 3 Part 2: Four-Layer Testing Framework, Data Contracts & SLA Monitoring

---

## 📌 Module Overview
This module covers enterprise software engineering practices applied to Data Engineering: implementing the **Four-Layer Pipeline Testing Framework** (Unit, Integration, Contract, Regression), enforcing **Data Contracts as Code using Pandera**, monitoring **SLA Contracts & Health Audits**, and walking through the Before/After production redesign of the **Razorpay Payment Pipeline**.

---

## 🧪 1. The Four-Layer Pipeline Testing Pyramid

To ensure pipeline stability and prevent breaking schema changes from degrading downstream BI reports, data engineering teams implement four distinct test layers.

```
                         TESTING PYRAMID
                         
                   / \
                  /   \  Layer 4: Regression Tests (Golden Dataset)
                 /-----\
                /       \  Layer 3: Contract Tests (Pandera Schemas)
               /---------\
              /           \  Layer 2: Integration Tests (Pipeline Flow)
             /-------------\
            /               \  Layer 1: Unit Tests (Isolated Functions)
           /-----------------\
```

### Layer Breakdown

#### Layer 1: Unit Tests
- **Focus**: Pure Python transformation functions, string parsers, date formatters, and math calculations in isolated memory.
- **Example**: Testing that `clean_phone_number("98765-01234")` returns `"+919876501234"`.

#### Layer 2: Integration Tests
- **Focus**: End-to-end execution flow from raw SQLite tables through Silver transformations to Gold aggregate insertion.
- **Example**: Verifying that calling `run_part1_demos()` actually populates `silver_customers` with correct row counts.

#### Layer 3: Contract Tests (Pandera)
- **Focus**: Schema contracts as code enforcing column data types, NULL constraints, value ranges, and regex formats before writing data to target tables.

#### Layer 4: Regression Tests (Golden Dataset)
- **Focus**: Comparing pipeline outputs against a static, human-verified "Golden Dataset" baseline (seed 42) to catch subtle logic bugs or metric shifts.

---

## 📜 2. Data Contracts as Code with Pandera

A **Data Contract** is a formal agreement between data producers (source microservices) and data consumers (data engineering & analytics). Using **Pandera**, schema validation is expressed in code:

```python
import pandera.pandas as pa

# Define Silver Customer Schema Contract
SilverCustomerContract = pa.DataFrameSchema({
    "customer_id": pa.Column(int, nullable=False, unique=True),
    "email": pa.Column(str, pa.Check.str_matches(r"^[\w\.-]+@[\w\.-]+\.\w+$"), nullable=True),
    "city": pa.Column(str, nullable=False),
    "state": pa.Column(str, pa.Check.str_length(2, 2)), # 2-letter state code e.g. 'KA'
    "version": pa.Column(int, pa.Check.greater_than_or_equal_to(1))
})

# Execute Contract Validation
def validate_and_write(df):
    try:
        validated_df = SilverCustomerContract.validate(df)
        write_to_database(validated_df)
    except pa.errors.SchemaError as err:
        log_and_route_to_dlq(err)
```

---

## 📈 3. SLA Contracts & Pipeline Health Monitoring

Production pipelines operate under strict **Service Level Agreements (SLAs)** monitored via audit tracking tables:

```sql
CREATE TABLE pipeline_run_audit (
    run_id TEXT PRIMARY KEY,
    pipeline_id TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    status TEXT NOT NULL,                -- 'RUNNING', 'SUCCESS', 'FAILED', 'SLA_BREACH'
    records_extracted INTEGER DEFAULT 0,
    records_loaded INTEGER DEFAULT 0,
    records_rejected INTEGER DEFAULT 0,
    error_summary TEXT
);
```

### Critical SLA Metrics
1. **Freshness SLA**: Time elapsed since last successful watermark update ($T_{\text{now}} - T_{\text{last\_success}} < \text{SLA\_threshold}$).
2. **Completeness SLA**: Reconciled row count ($\text{Extracted Rows} = \text{Loaded Rows} + \text{Rejected Rows}$).
3. **Duration SLA**: Total execution runtime in seconds.

---

## 💳 4. Case Study: Razorpay Payment Pipeline Production Redesign

### Before Redesign (Brittle Legacy State)
- Single monolithic Python script with hardcoded SQL query strings.
- Silent exception blocks (`except: pass`) dropping failed transactions without logging.
- No rate limiting or retries during API network timeouts.
- Raw credit card details saved directly in unencrypted local CSV files.

### After Redesign (Production Enterprise Architecture)
- Metadata-driven ingestion engine configured via `pipelines.yaml`.
- PII masking vault hashing card tokens using SHA-256 before storage.
- Exponential backoff with full jitter on HTTP 429 rate limit responses.
- Pandera contract validation isolating corrupted API payloads to a DLQ table.
- Complete execution audit logging in `pipeline_run_audit`.
