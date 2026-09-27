from typing import Dict, Any, List
from src.logging_utils import logger
from src.progress_tracker import ProgressTracker

class AssessmentEngine:
    def __init__(self):
        self.tracker = ProgressTracker()

    def run_assessment(self, week: int, non_interactive: bool = True) -> Dict[str, Any]:
        logger.info(f"Running Week {week} Scenario-Based Assessment (non_interactive={non_interactive})...")
        
        scenarios = {
            1: {
                "title": "HDFC Bank & Swiggy Data Movement Redesign",
                "challenge": "Choose ingestion patterns for HDFC core transactions vs Swiggy delivery stream.",
                "solution": "HDFC -> Full/Incremental ETL with pre-load PII masking; Swiggy -> Kafka streaming micro-batches.",
                "score": 100.0
            },
            2: {
                "title": "Puma India & Lenskart Star Schema & SCD2 Evaluation",
                "challenge": "Design Star Schema for order items and handle customer address changes without losing history.",
                "solution": "Star Schema with fact_order_item grain and dim_customer SCD Type 2 history records.",
                "score": 100.0
            },
            3: {
                "title": "Razorpay Payment Pipeline DLQ Isolation & 4-Layer Testing",
                "challenge": "Handle bad payment rows and prevent regressions on production pipelines.",
                "solution": "Isolate negative/null amounts to rejected_records DLQ table; run Golden Dataset regression tests.",
                "score": 100.0
            },
            4: {
                "title": "Flipkart Enterprise Architecture & DPDP/GDPR Compliance",
                "challenge": "Orchestrate 6 sources via metadata and enforce Gold layer PII vault protection.",
                "solution": "Metadata-driven ingestion loop using pipeline_control; mask emails/phones and compute SHA-256 hashes.",
                "score": 100.0
            }
        }
        
        assessment = scenarios.get(week, scenarios[1])
        
        self.tracker.record_activity(
            week=week,
            part=2,
            lesson_id=f"assessment_week_{week}",
            status="COMPLETED",
            score=assessment["score"],
            weak_topics=[]
        )
        
        return {
            "week": week,
            "title": assessment["title"],
            "challenge": assessment["challenge"],
            "solution": assessment["solution"],
            "score": assessment["score"],
            "status": "PASSED"
        }
