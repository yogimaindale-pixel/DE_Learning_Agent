# Week 4 Part 1: Orchestration & Metadata-Driven ETL

## Objectives
- Master Apache Airflow architecture: DAGs, TaskGroups, Dynamic Task Mapping, ExternalTaskSensors, and Cross-DAG dependencies.
- Build a generic metadata-driven ingestion engine using `pipeline_control_table`.
- Scale pipelines to N sources without writing custom DAG/engine code.

## 1. Metadata-Driven Ingestion Engine Architecture

Rather than writing hardcoded scripts for each of the 50+ data sources, enterprise platforms maintain a control table:

```sql
CREATE TABLE pipeline_control (
    pipeline_id TEXT PRIMARY KEY,
    pipeline_name TEXT,
    source_type TEXT, -- sqlite_oltp, csv, json, mock_api, kafka_ndjson
    target_table TEXT,
    last_watermark TEXT,
    is_active INTEGER
);
```

The generic engine loops through active control records, dynamically instantiates appropriate extractors and loaders, and updates run audit logs automatically.

---

## 2. Airflow Patterns at Scale
- **TaskGroup**: Groups related Bronze ingestion tasks cleanly in the UI.
- **Dynamic Task Mapping**: Expands tasks at runtime based on dynamic source lists (`.expand()`).
- **ExternalTaskSensor**: Blocks Gold summary DAG execution until upstream Silver processing DAG succeeds.
- **Fan-out / Fan-in**: Ingests 6 sources in parallel (fan-out) -> runs centralized Quality Gate check before publishing to Gold (fan-in).
