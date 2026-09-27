import random
from typing import Dict, Any, List, Optional
from src.logging_utils import logger
from src.progress_tracker import ProgressTracker

QUIZ_BANK = {
    1: [
        {
            "id": "q1_01",
            "type": "conceptual",
            "question": "In the HDFC Bank vs Meesho scenario, why does HDFC use traditional ETL while Meesho prefers ELT?",
            "options": [
                "A) HDFC requires pre-load data masking and strict transformation compliance before storing in warehouse, while Meesho leverages cheap lakehouse cloud compute to transform post-load",
                "B) HDFC has lower security requirements than Meesho",
                "C) ELT is only used for small flat files",
                "D) ETL cannot connect to relational databases"
            ],
            "answer": "A",
            "explanation": "HDFC is a regulated financial institution requiring PII/PCI security transformation before writing to warehouse storage. Meesho uses ELT to rapidly dump raw data into a data lake/warehouse and scale transformations on-demand."
        },
        {
            "id": "q1_02",
            "type": "code_reasoning",
            "question": "What is the primary purpose of tracking 'last_run_ts' in a pipeline_control watermark table?",
            "options": [
                "A) To measure pipeline execution speed",
                "B) To filter source extraction queries with 'WHERE updated_at > last_run_ts' for incremental loading",
                "C) To format dates into YYYY-MM-DD",
                "D) To delete old records from the target database"
            ],
            "answer": "B",
            "explanation": "The watermark pattern uses the recorded timestamp of the previous successful run to fetch only new or modified rows from the source system."
        },
        {
            "id": "q1_03",
            "type": "troubleshooting",
            "question": "When fetching payment records from Stripe/Razorpay REST API, your pipeline receives an HTTP 429 status code. What is the correct handling mechanism?",
            "options": [
                "A) Immediately crash the pipeline and alert on-call",
                "B) Ignore the response and retry infinitely in a tight loop",
                "C) Apply Exponential Backoff with jitter and retry up to max_retries before marking transient failure",
                "D) Delete the API credentials and request new ones"
            ],
            "answer": "C",
            "explanation": "HTTP 429 indicates Rate Limiting. Exponential backoff increases delay between retries to allow rate limits to reset."
        },
        {
            "id": "q1_04",
            "type": "design",
            "question": "Which ingestion pattern is best suited for real-time delivery tracking in Swiggy, Zepto, or CRED?",
            "options": [
                "A) Full Load CSV dump every midnight",
                "B) Streaming micro-batches / event-driven ingestion via Kafka/Kinesis",
                "C) Weekly manual SQL dump",
                "D) Periodic snapshot fact loading"
            ],
            "answer": "B",
            "explanation": "Real-time location and delivery status tracking requires sub-second or low-latency event streaming."
        },
        {
            "id": "q1_05",
            "type": "conceptual",
            "question": "In Medallion storage architecture, what is the role of the Silver layer?",
            "options": [
                "A) Raw, untouched source dumps",
                "B) Cleansed, validated, normalized, and PII-masked staging data",
                "C) Aggregated executive dashboards only",
                "D) Archival tape backups"
            ],
            "answer": "B",
            "explanation": "The Silver layer cleanses, filters, validates schema contracts, and masks sensitive PII data."
        }
    ],
    2: [
        {
            "id": "q2_01",
            "type": "conceptual",
            "question": "In dimensional modeling, what is the key difference between Star Schema and Snowflake Schema?",
            "options": [
                "A) Star schema denormalizes dimensions into single tables; Snowflake normalizes dimensions into sub-dimension tables",
                "B) Star schema has no fact tables",
                "C) Snowflake schema does not support surrogate keys",
                "D) Star schema is only used in MongoDB"
            ],
            "answer": "A",
            "explanation": "Star schemas simplify query joins by keeping dimensions denormalized, whereas Snowflake normalizes dimension hierarchies."
        },
        {
            "id": "q2_02",
            "type": "code_reasoning",
            "question": "What happens when SCD Type 2 is implemented upon a customer address change?",
            "options": [
                "A) The existing address column in dim_customer is overwritten",
                "B) The old record's expiry_date and is_current flag are updated, and a new record with a new surrogate key is inserted",
                "C) A new column previous_address is added to dim_customer",
                "D) All historical fact records are deleted"
            ],
            "answer": "B",
            "explanation": "SCD Type 2 preserves history by expiring the active version (is_current=0) and inserting a new version (is_current=1, version=N+1)."
        },
        {
            "id": "q2_03",
            "type": "troubleshooting",
            "question": "Why is generating surrogate keys using 'SELECT MAX(surrogate_key) + 1' dangerous in a production environment?",
            "options": [
                "A) It is slower than writing to text files",
                "B) Parallel pipeline runs can evaluate the same MAX value concurrently, causing duplicate primary key collisions",
                "C) It automatically deletes foreign keys",
                "D) It only works on dates"
            ],
            "answer": "B",
            "explanation": "MAX+1 suffers from severe race conditions under concurrent execution. Auto-increment or deterministic hash surrogate keys should be used instead."
        },
        {
            "id": "q2_04",
            "type": "design",
            "question": "In the Lenskart prescription analytics star schema, why is customer_sk = -1 used in fact rows when customer details are unavailable?",
            "options": [
                "A) To intentionally corrupt the report",
                "B) To satisfy foreign key integrity without discarding facts using the Unknown Member pattern",
                "C) Because SQLite does not support NULLs",
                "D) To indicate a deleted order"
            ],
            "answer": "B",
            "explanation": "The Unknown Member pattern (-1 surrogate key) prevents losing financial facts when dimension metadata is delayed or missing."
        },
        {
            "id": "q2_05",
            "type": "code_reasoning",
            "question": "Which SQL window function ranks rows sequentially without gaps (e.g. 1, 2, 2, 3)?",
            "options": [
                "A) ROW_NUMBER()",
                "B) RANK()",
                "C) DENSE_RANK()",
                "D) NTILE(4)"
            ],
            "answer": "C",
            "explanation": "DENSE_RANK() produces consecutive rank numbers without leaving gaps after tied values."
        }
    ],
    3: [
        {
            "id": "q3_01",
            "type": "conceptual",
            "question": "How are incoming pipeline errors properly categorized in a production ETL framework?",
            "options": [
                "A) All errors are ignored",
                "B) Transient errors -> Retry with backoff; Data errors -> Quarantine to DLQ; Schema errors -> HALT pipeline",
                "C) All errors halt the pipeline immediately",
                "D) All errors overwrite the target database"
            ],
            "answer": "B",
            "explanation": "Transient issues (network glitches) should retry; invalid row data should be quarantined without stopping good rows; schema drift requires structural intervention."
        },
        {
            "id": "q3_02",
            "type": "code_reasoning",
            "question": "What information MUST be recorded in a Dead Letter Queue (DLQ) table?",
            "options": [
                "A) Raw payload, reason code, error details, pipeline run ID, and timestamp",
                "B) Database password only",
                "C) Employee salaries",
                "D) Executable Python bytecode"
            ],
            "answer": "A",
            "explanation": "A complete DLQ audit record requires raw input, failure reason, error message, run ID, and creation timestamp for replay."
        },
        {
            "id": "q3_03",
            "type": "troubleshooting",
            "question": "In the Razorpay payment pipeline, a regression test fails on a golden dataset comparison. What does this indicate?",
            "options": [
                "A) The database server is powered off",
                "B) A code or logic change altered output calculation results compared to verified baseline expectations",
                "C) The Python compiler was updated",
                "D) The network speed increased"
            ],
            "answer": "B",
            "explanation": "Golden dataset regression testing ensures new pipeline versions produce identical outputs for verified input baselines."
        },
        {
            "id": "q3_04",
            "type": "design",
            "question": "Which tool enables declarative 'schema validation as code' for data contracts in Python?",
            "options": [
                "A) Pandera",
                "B) Flask",
                "C) Django",
                "D) NumPy"
            ],
            "answer": "A",
            "explanation": "Pandera allows defining statistical and structural schema contracts directly in Python code."
        }
    ],
    4: [
        {
            "id": "q4_01",
            "type": "conceptual",
            "question": "How does a metadata-driven ETL engine achieve scale across N data sources?",
            "options": [
                "A) By writing unique custom Python code for every source",
                "B) By reading source configs from pipeline_control table and executing a generic parameter-driven pipeline loop",
                "C) By manually running SQL scripts in command line",
                "D) By disabling audit logging"
            ],
            "answer": "B",
            "explanation": "Metadata-driven design decouples orchestration logic from source definitions, allowing new sources to be onboarded simply by adding config rows."
        },
        {
            "id": "q4_02",
            "type": "design",
            "question": "In compliance with the DPDP Act and GDPR, how should direct PII (email, phone) be treated before publishing to Gold analytics tables?",
            "options": [
                "A) Published in clear plain text",
                "B) Excluded, masked, or anonymized using SHA-256 hashing and token vault reference",
                "C) Saved into public GitHub repositories",
                "D) Converted into uppercase"
            ],
            "answer": "B",
            "explanation": "Gold analytics tables should contain aggregated business metrics and anonymized/pseudonymized keys, never direct raw PII."
        },
        {
            "id": "q4_03",
            "type": "troubleshooting",
            "question": "In SQLite, what does 'EXPLAIN QUERY PLAN' reveal when an unindexed table is queried with a WHERE clause?",
            "options": [
                "A) SCAN TABLE (full table scan)",
                "B) SEARCH TABLE USING INDEX",
                "C) MEMORY OVERFLOW",
                "D) DISK FORMAT ERROR"
            ],
            "answer": "A",
            "explanation": "Unindexed queries perform a full SCAN TABLE, reading every row sequentially. Creating an index changes execution to SEARCH TABLE USING INDEX."
        }
    ]
}

class QuizEngine:
    def __init__(self):
        self.tracker = ProgressTracker()

    def run_quiz(self, week: int, count: int = 10, non_interactive: bool = False) -> Dict[str, Any]:
        questions = QUIZ_BANK.get(week, QUIZ_BANK[1])
        if count < len(questions):
            selected = random.sample(questions, count)
        else:
            selected = questions
            
        correct = 0
        total = len(selected)
        weak_topics = []
        
        logger.info(f"Starting Week {week} Quiz ({total} questions, non_interactive={non_interactive})...")
        
        for idx, q in enumerate(selected, 1):
            if non_interactive:
                # Deterministic selection for non-interactive automated test run
                user_ans = q["answer"]
            else:
                print(f"\nQuestion {idx}/{total} [{q['type'].upper()}]: {q['question']}")
                for opt in q["options"]:
                    print(f"  {opt}")
                user_ans = input("Your answer (A/B/C/D): ").strip().upper()
                
            if user_ans == q["answer"]:
                correct += 1
            else:
                weak_topics.append(q["type"])
                
        score_pct = round((correct / total) * 100.0, 2)
        status = "COMPLETED" if score_pct >= 80.0 else "IN_PROGRESS"
        
        self.tracker.record_activity(
            week=week,
            part=1,
            lesson_id=f"quiz_week_{week}",
            status=status,
            score=score_pct,
            weak_topics=list(set(weak_topics))
        )
        
        return {
            "week": week,
            "total_questions": total,
            "correct": correct,
            "score_pct": score_pct,
            "status": status,
            "weak_topics": list(set(weak_topics))
        }
