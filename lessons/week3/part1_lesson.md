# Week 3 Part 1: Production Pipeline Patterns & Error Handling

## Objectives
- Implement production load patterns: Append-Only, Incremental Upsert/Merge, and Full Swap.
- Deep dive into CDC capture mechanisms: Trigger, Snapshot Diff, and Log-based (Debezium/Kafka).
- Classify pipeline errors into Transient, Data, and Schema error classes.
- Build Dead Letter Queues (DLQ) with error codes, payload isolation, and replay capability.

## 1. Error Classification Framework

```
                          Incoming Pipeline Error
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
  [ Transient Error ]         [ Data Error ]              [ Schema Error ]
 (Network/API Rate Limit)    (Invalid Email, Negative)    (Drift/Missing Column)
         │                           │                           │
         ▼                           ▼                           ▼
Exponential Backoff Retry   Isolate to DLQ Table        HALT Pipeline & Alert
(max_retries = 3)          (rejected_records)          On-Call Data Engineer
```

---

## 2. Dead Letter Queue (DLQ) Pattern
When invalid records fail data contract validation:
1. Do NOT crash the entire batch pipeline.
2. Isolate bad rows into `rejected_records` with fields: `run_id`, `pipeline_id`, `raw_payload`, `reason_code`, `error_details`, `created_at`.
3. Allow operational teams to inspect, fix payload, and execute `replay_dlq()` pipeline step.
