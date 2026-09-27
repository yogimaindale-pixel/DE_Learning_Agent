# Week 4 Part 1: Enterprise Airflow Orchestration & Metadata-Driven Pipeline Frameworks

---

## 📌 Module Overview
This module covers enterprise workflow orchestration with **Apache Airflow**, advanced DAG design patterns (**Dynamic Task Mapping, TaskGroups, ExternalTaskSensors, Cross-DAG dependencies**), and building a scalable, generic **Metadata-Driven Ingestion Engine** that scales to $N$ source systems using a central control table.

---

## 🌀 1. Apache Airflow Core Architecture & Execution Model

**Apache Airflow** is an open-source workflow orchestration platform where pipelines are defined as **Directed Acyclic Graphs (DAGs)** in Python code.

```
                                 AIRFLOW ARCHITECTURE
                                 
      +------------------+      +-----------------------+      +------------------+
      | Airflow Web UI   | ---> | Metadata Database     | <--- | Airflow Scheduler|
      | (DAG Monitoring) |      | (PostgreSQL / MySQL)  |      | (Parses DAGs)    |
      +------------------+      +-----------------------+      +------------------+
                                                                         |
                                                                         v
                                                               +------------------+
                                                               | Celery / K8s     |
                                                               | Worker Pool      |
                                                               +------------------+
```

### Core Concepts
- **DAG (Directed Acyclic Graph)**: Collection of all tasks, organized with explicit directional dependencies (`task_a >> task_b`), executing on a schedule without circular loops.
- **Operator**: Template for a single task (e.g., `PythonOperator`, `BashOperator`, `SQLExecuteQueryOperator`).
- **Task Instance**: A specific execution of a task for a given DAG run execution date.
- **Backfill & Catchup**: Re-running DAGs for historical dates after pipeline maintenance.

---

## 🌿 2. Advanced Airflow Design Patterns

```
   FAN-OUT (Dynamic Task Mapping)             FAN-IN (Quality Gate Consolidation)
          [Extract Metadata]                          [Ingest Table A]
             /    |    \                                     \
            v     v     v                                     v
       [Table A][Table B][Table C]                  [Consolidated Quality Check]
```

### Pattern A: Dynamic Task Mapping
- **Concept**: Automatically creates $N$ parallel task instances at runtime based on the result of an upstream task (e.g., reading active tables from `pipeline_control`).
- **Use Case**: Ingesting 50 database tables concurrently without hardcoding 50 separate task nodes in Python.

### Pattern B: TaskGroups
- **Concept**: Groups related tasks visually in the Airflow UI to organize complex DAG workflows.

### Pattern C: ExternalTaskSensor & Cross-DAG Dependencies
- **Concept**: Pauses execution of a downstream DAG (e.g., `Gold_Summary_DAG`) until an upstream dependency DAG (e.g., `Silver_Ingestion_DAG`) finishes successfully.

---

## ⚙️ 3. Metadata-Driven Ingestion Framework Pattern

In high-growth enterprises, writing custom Python scripts for every new source table leads to code duplication and technical debt.
A **Metadata-Driven Framework** replaces custom code with **1 Generic Engine + `pipeline_control` Metadata Table**.

```
+---------------------------------------------------------------------------------------+
| METADATA CONTROL TABLE: pipeline_control                                              |
+---------------+---------------------+-------------+--------------+--------------------+
| pipeline_id   | pipeline_name       | source_type | target_table | is_active          |
+---------------+---------------------+-------------+--------------+--------------------+
| p001          | customers_ingestion | csv         | silver_cust  | 1                  |
| p002          | orders_ingestion    | sqlite_oltp | silver_ord   | 1                  |
+---------------+---------------------+-------------+--------------+--------------------+
                                          |
                                          v
                    +-------------------------------------------+
                    | SINGLE GENERIC INGESTION ENGINE           |
                    | (src/week4/part1_orchestration.py)        |
                    +-------------------------------------------+
                    Reads metadata -> Extracts -> Loads ANY src!
```

### Benefits of Metadata-Driven Architecture
1. **Onboarding Speed**: Adding a 51st table requires **one INSERT row into `pipeline_control`**—zero code changes or deployments required.
2. **Centralized Operational Control**: Disabling a failing pipeline is as simple as setting `UPDATE pipeline_control SET is_active = 0`.
3. **Unified Logging & Audit**: Standardized metrics and audit records populated across all pipelines automatically.
