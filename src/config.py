import os
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
DB_PATH = DATABASE_DIR / "learning_agent.db"
SQL_DIR = BASE_DIR / "sql"
LESSONS_DIR = BASE_DIR / "lessons"
EXERCISES_DIR = BASE_DIR / "exercises"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

def load_yaml_config(filename: str) -> dict:
    filepath = CONFIG_DIR / filename
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def get_course_config() -> dict:
    return load_yaml_config("course.yaml")

def get_pipelines_config() -> dict:
    return load_yaml_config("pipelines.yaml")

def get_data_contracts() -> dict:
    return load_yaml_config("data_contracts.yaml")
