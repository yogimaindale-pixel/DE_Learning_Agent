import argparse
import json
import sys
from src.database import init_db
from src.data_generator import generate_all_data
from src.lesson_engine import LessonEngine
from src.quiz_engine import QuizEngine
from src.assessment_engine import AssessmentEngine
from src.progress_tracker import ProgressTracker
from src.capstone.flipkart_analytics import run_capstone
from src.config import get_course_config
from src.logging_utils import logger

def main():
    parser = argparse.ArgumentParser(description="DE_Learning_Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available actions")

    # init
    subparsers.add_parser("init", help="Initialize SQLite DB and generate reproducible synthetic data (seed 42)")

    # syllabus
    subparsers.add_parser("syllabus", help="Display course syllabus overview")

    # learn
    p_learn = subparsers.add_parser("learn", help="Run lesson and theory walkthrough")
    p_learn.add_argument("--week", type=int, required=True, help="Week number (1-4)")
    p_learn.add_argument("--part", type=int, default=1, help="Part number (1-2)")

    # demo
    p_demo = subparsers.add_parser("demo", help="Run code demonstration")
    p_demo.add_argument("--week", type=int, required=True, help="Week number (1-4)")
    p_demo.add_argument("--part", type=int, default=1, help="Part number (1-2)")
    p_demo.add_argument("--topic", type=str, default=None, help="Topic filter")

    # lab
    p_lab = subparsers.add_parser("lab", help="Run hands-on guided lab")
    p_lab.add_argument("--week", type=int, required=True, help="Week number (1-4)")
    p_lab.add_argument("--part", type=int, default=1, help="Part number (1-2)")

    # quiz
    p_quiz = subparsers.add_parser("quiz", help="Run module quiz")
    p_quiz.add_argument("--week", type=int, required=True, help="Week number (1-4)")
    p_quiz.add_argument("--count", type=int, default=10, help="Number of questions")
    p_quiz.add_argument("--non-interactive", action="store_true", help="Run non-interactively")

    # assess
    p_assess = subparsers.add_parser("assess", help="Run scenario assessment")
    p_assess.add_argument("--week", type=int, required=True, help="Week number (1-4)")
    p_assess.add_argument("--non-interactive", action="store_true", help="Run non-interactively")

    # capstone
    p_capstone = subparsers.add_parser("capstone", help="Execute Flipkart Analytics Capstone")
    p_capstone.add_argument("--step", type=str, default="all", help="Capstone step (all, ingest, medallion, quality, analytics)")

    # progress
    subparsers.add_parser("progress", help="View learner progress summary")

    # reset
    p_reset = subparsers.add_parser("reset", help="Reset progress or database state")
    p_reset.add_argument("--scope", type=str, default="progress", choices=["progress", "audit", "all"], help="Reset scope")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    lesson_engine = LessonEngine()
    quiz_engine = QuizEngine()
    assessment_engine = AssessmentEngine()
    progress_tracker = ProgressTracker()

    if args.command == "init":
        init_db()
        generate_all_data()
        print("Initialization complete. SQLite database initialized & synthetic dataset generated (seed=42).")

    elif args.command == "syllabus":
        cfg = get_course_config()
        print(f"\n================ {cfg['course']['title']} (v{cfg['course']['version']}) ================\n")
        for w in cfg['course']['weeks']:
            print(f"Week {w['number']}: {w['title']}")
            for p in w['parts']:
                print(f"  Part {p['number']}: {p['title']}")
                for t in p['topics']:
                    print(f"    - {t}")
        print("\nFinal Capstone:", cfg['capstone']['title'])
        for d in cfg['capstone']['deliverables']:
            print(f"  * {d}")
        print("\n" + "="*70)

    elif args.command == "learn":
        content = lesson_engine.load_lesson_markdown(args.week, args.part)
        print(f"\n--- WEEK {args.week} PART {args.part} LESSON ---\n")
        print(content[:1500] + "\n\n[... Full theory lesson displayed ...]")
        progress_tracker.record_activity(args.week, args.part, f"lesson_w{args.week}p{args.part}", "COMPLETED", 100.0)

    elif args.command == "demo" or args.command == "lab":
        res = lesson_engine.run_part_demonstration(args.week, args.part, getattr(args, 'topic', None))
        print(json.dumps(res, indent=2))
        progress_tracker.record_activity(args.week, args.part, f"{args.command}_w{args.week}p{args.part}", "COMPLETED", 100.0)

    elif args.command == "quiz":
        res = quiz_engine.run_quiz(args.week, count=args.count, non_interactive=args.non_interactive)
        print(json.dumps(res, indent=2))

    elif args.command == "assess":
        res = assessment_engine.run_assessment(args.week, non_interactive=args.non_interactive)
        print(json.dumps(res, indent=2))

    elif args.command == "capstone":
        res = run_capstone(step=args.step)
        print(json.dumps(res, indent=2))

    elif args.command == "progress":
        res = progress_tracker.get_progress_summary()
        print("\n================ LEARNER PROGRESS SUMMARY ================")
        print(f"Total Completed Lessons/Quizzes: {res['total_completed']}")
        print(f"Average Score: {res['avg_score']:.2f}%")
        if res["weak_topics_summary"]:
            print(f"Weak Topics to Review: {', '.join(res['weak_topics_summary'])}")
        print("-" * 58)
        for l in res["lessons"]:
            print(f"Week {l['week']} Part {l['part']} | {l['lesson_id']:<20} | Status: {l['status']:<10} | Score: {l['score']:.1f}%")
        print("==========================================================")

    elif args.command == "reset":
        progress_tracker.reset_progress(scope=args.scope)
        print(f"Reset action complete for scope: {args.scope}")

if __name__ == "__main__":
    main()
