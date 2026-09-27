from typing import Dict, Any, List, Optional
import sqlite3
from src.database import get_connection, query_db, execute_query
from src.logging_utils import logger

class ProgressTracker:
    def __init__(self):
        pass

    def record_activity(
        self,
        week: int,
        part: int,
        lesson_id: str,
        status: str,
        score: float = 0.0,
        weak_topics: Optional[List[str]] = None
    ) -> None:
        weak_topics_str = ",".join(weak_topics) if weak_topics else ""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT attempts, score FROM user_progress WHERE week = ? AND part = ? AND lesson_id = ?;
            """, (week, part, lesson_id))
            row = cursor.fetchone()
            if row:
                attempts = row["attempts"] + 1
                new_score = max(row["score"], score)
                cursor.execute("""
                    UPDATE user_progress
                    SET status = ?, score = ?, attempts = ?, weak_topics = ?, last_accessed = CURRENT_TIMESTAMP
                    WHERE week = ? AND part = ? AND lesson_id = ?;
                """, (status, new_score, attempts, weak_topics_str, week, part, lesson_id))
            else:
                cursor.execute("""
                    INSERT INTO user_progress (week, part, lesson_id, status, score, attempts, weak_topics)
                    VALUES (?, ?, ?, ?, ?, 1, ?);
                """, (week, part, lesson_id, status, score, weak_topics_str))
            conn.commit()
        finally:
            conn.close()

    def get_progress_summary(self) -> Dict[str, Any]:
        rows = query_db("SELECT week, part, lesson_id, status, score, attempts, weak_topics FROM user_progress;")
        summary = {
            "total_completed": 0,
            "total_score": 0.0,
            "lessons": [],
            "weak_topics_summary": []
        }
        all_weak = []
        for r in rows:
            summary["lessons"].append(dict(r))
            if r["status"] == "COMPLETED":
                summary["total_completed"] += 1
                summary["total_score"] += r["score"]
            if r["weak_topics"]:
                all_weak.extend([wt.strip() for wt in r["weak_topics"].split(",") if wt.strip()])
                
        summary["weak_topics_summary"] = list(set(all_weak))
        summary["avg_score"] = (summary["total_score"] / summary["total_completed"]) if summary["total_completed"] > 0 else 0.0
        return summary

    def reset_progress(self, scope: str = "progress") -> None:
        if scope in ["progress", "all"]:
            execute_query("DELETE FROM user_progress;")
            logger.info("User progress reset.")
        if scope in ["audit", "all"]:
            execute_query("DELETE FROM pipeline_run_audit;")
            execute_query("DELETE FROM data_quality_results;")
            execute_query("DELETE FROM rejected_records;")
            logger.info("Pipeline audit and quality logs reset.")
