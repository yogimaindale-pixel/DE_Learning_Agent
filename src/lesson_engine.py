from pathlib import Path
from typing import Dict, Any, Optional
from src.config import LESSONS_DIR
from src.logging_utils import logger
from src.week1.part1_etl_fundamentals import run_part1_demos as run_w1p1
from src.week1.part2_storage_movement import run_part2_demos as run_w1p2
from src.week2.part1_dimensional_modeling import run_part1_demos as run_w2p1
from src.week2.part2_scd_surrogate_keys import run_part2_demos as run_w2p2
from src.week3.part1_production_etl import run_part1_demos as run_w3p1
from src.week3.part2_testing_monitoring import run_part2_demos as run_w3p2
from src.week4.part1_orchestration import run_part1_demos as run_w4p1
from src.week4.part2_quality_privacy_performance import run_part2_demos as run_w4p2

class LessonEngine:
    def __init__(self):
        pass

    def load_lesson_markdown(self, week: int, part: int) -> str:
        filepath = LESSONS_DIR / f"week{week}" / f"part{part}_lesson.md"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return f"# Week {week} Part {part} Lesson\n\nLesson content loading..."

    def run_part_demonstration(self, week: int, part: int, topic: Optional[str] = None) -> Dict[str, Any]:
        if week == 1 and part == 1:
            return run_w1p1()
        elif week == 1 and part == 2:
            return run_w1p2()
        elif week == 2 and part == 1:
            return run_w2p1()
        elif week == 2 and part == 2:
            return run_w2p2()
        elif week == 3 and part == 1:
            return run_w3p1()
        elif week == 3 and part == 2:
            return run_w3p2()
        elif week == 4 and part == 1:
            return run_w4p1()
        elif week == 4 and part == 2:
            return run_w4p2()
        return {"msg": f"Demonstration for Week {week} Part {part} executed."}
