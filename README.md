# DE_Learning_Agent - Data Engineering Learning Agent & CLI

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**DE_Learning_Agent** is an interactive, deterministic, local Data Engineering learning platform and CLI application built in Python and SQL. It uses synthetic reproducible datasets (random seed `42`) to teach enterprise data engineering concepts, production pipeline design, testing frameworks, privacy compliance, and dimensional modeling through hands-on labs, code demonstrations, quizzes, scenario-based assessments, and a comprehensive analytics capstone.

---

## Table of Contents
1. [Project Structure](#project-structure)
2. [Quickstart & Setup](#quickstart--setup)
3. [CLI Reference](#cli-reference)
4. [Chapter-by-Chapter Course Syllabus & Concepts](#chapter-by-chapter-course-syllabus--concepts)
   - [Week 1: ETL Fundamentals & Data Movement](#week-1-etl-fundamentals--data-movement)
   - [Week 2: Transformation Design Patterns](#week-2-transformation-design-patterns)
   - [Week 3: Production ETL Design & Development](#week-3-production-etl-design--development)
   - [Week 4: Enterprise Pipeline Architecture](#week-4-enterprise-pipeline-architecture)
   - [Final Capstone: Flipkart Order Analytics Platform](#final-capstone-flipkart-order-analytics-platform)
5. [Testing & Quality Assurance](#testing--quality-assurance)

---

## Project Structure

```text
DE_Learning_Agent/
├── config/                  # YAML configurations (course, pipelines, data contracts)
│   ├── course.yaml
│   ├── pipelines.yaml
│   └── data_contracts.yaml
├── data/                    # Medallion storage directories
│   ├── raw/                 # Raw CSVs, JSONs, mock API payloads, Kafka streams
│   ├── staging/             # Cleaned Parquet / JSON intermediate files
│   ├── curated/             # Aggregated Gold outputs
│   ├── serving/             # Serving layer
│   └── quarantine/          # Dead Letter Queue (DLQ) rejected payloads
├── database/                # SQLite local data warehouse
│   └── learning_agent.db
├── sql/                     # Pure SQL DDL and analytical scripts
│   ├── ddl/                 # Audit, OLTP, Medallion, Star Schema DDLs
│   ├── transformations/     # SCD2 Merge, Upsert, Fact loading scripts
│   ├── quality/             # Data quality assertion queries
│   └── analytics/           # Analytical SQL queries
├── src/                     # Core Python engines & modules
│   ├── cli.py               # Argument parser and command router
│   ├── config.py            # Path and configuration loader
│   ├── database.py          # SQLite helper, DDL execution, transaction manager
│   ├── data_generator.py    # Synthetic reproducible data generator (seed 42)
│   ├── lesson_engine.py     # Theory & demonstration engine
│   ├── quiz_engine.py       # Interactive & non-interactive quiz engine
│   ├── assessment_engine.py # Scenario assessment engine
│   ├── progress_tracker.py  # User progress & score recorder
│   ├── logging_utils.py     # Structured logger & run audit tracking
│   ├── week1/               # Week 1 Python code & labs
│   ├── week2/               # Week 2 Python code & labs
│   ├── week3/               # Week 3 Python code & labs
│   ├── week4/               # Week 4 Python code & labs
│   └── capstone/            # Flipkart Order Analytics Platform capstone
├── lessons/                 # Chapter theory documentation in Markdown
├── exercises/               # Starter code with TODOs & reference solutions
├── tests/                   # 4-layer testing suite (Unit, Integration, Contract, Regression)
├── logs/                    # Execution logs
├── reports/                 # Execution & assessment reports
└── run_agent.py             # Main CLI entry point launcher
```

---

## Quickstart & Setup

### 1. Requirements
- Python 3.11+
- Virtual environment with `pandas`, `pyyaml`, `pytest`, `pandera`, `pyarrow`

### 2. Initialize Database & Generate Synthetic Data
```bash
python run_agent.py init
```
*Initializes SQLite schema in `database/learning_agent.db` and generates reproducible synthetic dataset using seed `42`.*

---

## CLI Reference

| Command | Usage | Description |
| :--- | :--- | :--- |
| `init` | `python run_agent.py init` | Initializes SQLite DB schema and populates synthetic data (seed 42) |
| `syllabus` | `python run_agent.py syllabus` | Displays course syllabus and week-by-week module breakdown |
| `learn` | `python run_agent.py learn --week 1 --part 1` | Displays theory lesson and walkthrough for specified week/part |
| `demo` | `python run_agent.py demo --week 1 --part 1` | Executes live Python & SQL code demonstrations |
| `lab` | `python run_agent.py lab --week 2 --part 2` | Runs hands-on lab exercise and prints execution results |
| `quiz` | `python run_agent.py quiz --week 3 --count 10 [--non-interactive]` | Runs module quiz with instant scoring and explanations |
| `assess` | `python run_agent.py assess --week 4 [--non-interactive]` | Runs scenario-based assessment evaluating real-world case studies |
| `capstone` | `python run_agent.py capstone --step all` | Executes the Flipkart Order Analytics Platform capstone |
| `progress` | `python run_agent.py progress` | Displays summary of completed modules, scores, and weak topics |
| `reset` | `python run_agent.py reset --scope progress` | Resets progress tracking or database audit logs |

---

## Chapter-by-Chapter Course Syllabus & Concepts

### Week 1: ETL Fundamentals & Data Movement

#### Part 1: ETL vs ELT & Ingestion Patterns
- **ETL vs ELT Trade-offs**:
  - *HDFC Bank Scenario (ETL)*: Regulated core banking requires in-flight PII/PCI masking and strict pre-load security transformations before data hits storage.
  - *Meesho Scenario (ELT)*: High-scale e-commerce marketplace dumps raw JSON/Parquet dumps into cloud lakes and performs scalable, elastic transformations post-load.
- **Ingestion Patterns**:
  - *Full Load*: Replaces target table completely; best for static small master data.
  - *Incremental Load*: Uses `updated_at` watermark column to fetch only new/modified rows.
  - *CDC (Change Data Capture)*: Captures row-level Insert (I), Update (U), and Delete (D) operations from database logs (Debezium).
  - *Streaming*: Low-latency micro-batch event streams for Swiggy, Zepto, CRED, and Hotstar live tracking.
- **REST API Pagination & Rate Limits**:
  - Demonstrates paginated API responses with offset/cursor pagination.
  - Handles **HTTP 429 Rate Limits** using Exponential Backoff with Jitter and checkpointing.

#### Part 2: Storage Layers & Data Movement
- **Medallion Architecture**:
  - *Bronze (Raw)*: Immutable append-only source dumps.
  - *Silver (Cleaned)*: Standardized types, deduplicated, PII masked, validated schemas.
  - *Gold (Curated)*: Denormalized star schema facts/dimensions and business aggregates.
- **File Format Benchmark**:
  - Compares storage efficiency and read performance across CSV, JSON, and Parquet columnar format.
- **Watermark Pattern**:
  - Tracks `last_run_ts` in `pipeline_control` table; advances timestamp only upon successful transaction commit.
- **SaaS Connectors**:
  - Normalizes export patterns from Salesforce, HubSpot, Workday, and SAP into canonical schema definitions.

---

### Week 2: Transformation Design Patterns

#### Part 1: Dimensional Modeling & Analytics SQL
- **Star vs Snowflake Schemas**:
  - Star schema denormalizes dimensions for simpler joins; Snowflake normalizes hierarchy levels.
- **Fact Table Types**:
  - *Transaction Fact*: Atomic purchase events (`fact_order_item`).
  - *Periodic Snapshot Fact*: Periodic summaries (`fact_daily_sales_snapshot`).
  - *Accumulating Snapshot Fact*: Workflow lifecycle milestones (`fact_delivery_lifecycle`).
- **Join Anti-Patterns & Fan-Out Diagnosis**:
  - Identifies double-counting caused by 1-to-N join fan-out before aggregation in Puma India, BigBasket, Nykaa, and Amazon India case studies.
- **Advanced SQL Window Functions**:
  - Demonstrates `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `LAG()`, `LEAD()`, `NTILE()`, and running `SUM() OVER()`.

#### Part 2: Slowly Changing Dimensions (SCD) & Surrogate Keys
- **SCD Types**:
  - *Type 1*: Overwrite attribute (typo correction).
  - *Type 2*: Maintain history with `effective_date`, `expiry_date`, `is_current`, and `version`.
  - *Type 3*: Add `previous_column` (tracks single prior state).
- **Surrogate Keys & Concurrency Risk**:
  - Demonstrates why `SELECT MAX(sk) + 1` causes duplicate key collisions under parallel runs.
  - Promotes AUTOINCREMENT, SHA-256 hash surrogate keys, and `dim_date` integer keys (`YYYYMMDD`).
- **Lenskart Capstone**:
  - Star schema design for prescription analytics (`dim_prescription`).

---

### Week 3: Production ETL Design & Development

#### Part 1: Production Pipeline Patterns & Error Handling
- **Load Strategies**:
  - *Append-Only*: Immutable audit logging.
  - *Incremental Merge/Upsert*: Atomic SQLite `INSERT ... ON CONFLICT DO UPDATE`.
  - *Full Swap*: Atomic table swap via transactions.
- **Error Classification**:
  - *Transient*: Network timeouts / API rate limits -> Retry with exponential backoff.
  - *Data Error*: Bad formatting / negative values -> Isolate to Dead Letter Queue (`rejected_records`).
  - *Schema Error*: Column missing or drift -> HALT pipeline immediately.
- **Dead Letter Queue (DLQ) & Replay**:
  - Isolates bad rows with reason codes, error details, and raw payload; provides automated DLQ replay logic.

#### Part 2: Testing, Monitoring & SLA Management
- **4-Layer Testing Framework**:
  - *Unit Testing*: Function-level isolation.
  - *Integration Testing*: End-to-end component flow.
  - *Contract Testing*: Schema as code validation using Pandera.
  - *Regression Testing*: Output comparison against Golden Dataset baseline.
- **SLA Monitoring & Health Queries**:
  - Tracks Freshness, Completeness, Success Rate, and Throughput in `pipeline_run_audit`.
- **Razorpay Payment Pipeline Case Study**:
  - Before vs After production redesign comparison.

---

### Week 4: Enterprise Pipeline Architecture

#### Part 1: Orchestration & Metadata-Driven ETL
- **Apache Airflow Concepts**:
  - Dynamic Task Mapping, TaskGroups, ExternalTaskSensors, Cross-DAG dependencies, and Fan-out / Fan-in patterns.
- **Generic Metadata Engine**:
  - Driven by `pipeline_control` table; executes N sources dynamically without code modification.

#### Part 2: Data Quality, Privacy & Performance Optimization
- **Data Quality as Code**:
  - Declarative uniqueness and non-null gate assertions.
- **PII Vault & DPDP/GDPR Compliance**:
  - Column masking (`email -> c***i@example.com`, `phone -> ******3210`) and SHA-256 hashing.
  - Gold tables contain zero direct PII.
- **Performance Profiling**:
  - `EXPLAIN QUERY PLAN` profiling demonstrating full table scan reduction via index selection.
  - Materialized summary table refresh.

---

### Final Capstone: Flipkart Order Analytics Platform

Integrates **6 Source Styles**:
1. SQLite OLTP DB (`oltp_orders`, `oltp_customers`)
2. CSV Files (`products.csv`, `customers.csv`)
3. JSON Files (`app_events.json`, `saas_exports.json`)
4. Paginated Mock REST API (`mock_payments_api`)
5. Kafka NDJSON Event Stream (`delivery_stream.ndjson`)
6. SaaS Exports (`saas_exports.json`)

**6 Deliverables**:
1. Architecture and Data-Flow Document
2. Metadata-Driven Ingestion Framework
3. Bronze, Silver, and Gold Medallion Datasets
4. Automated Quality & PII Vault Controls
5. Analytics SQL & Performance Optimization Report
6. Tests, Runbook, and Mentor-Review Checklist

Execute via:
```bash
python run_agent.py capstone --step all
```

---

## Testing & Quality Assurance

Run the comprehensive pytest suite:
```bash
pytest -q
```

The test suite validates:
- `tests/unit/test_data_generator.py`: Synthetic data initialization and seed 42 reproducibility.
- `tests/integration/test_pipeline_flow.py`: End-to-end Medallion pipeline, Star schema loading, and Capstone execution.
- `tests/contract/test_data_contracts.py`: Pandera schema validation contracts as code.
- `tests/regression/test_golden_dataset.py`: Regression verification against Golden Dataset baselines.

---

## License
MIT License - Free for educational and learning purposes.
