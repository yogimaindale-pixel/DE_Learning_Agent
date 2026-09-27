-- Pipeline Control Table
CREATE TABLE IF NOT EXISTS pipeline_control (
    pipeline_id TEXT PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    target_table TEXT NOT NULL,
    last_watermark TEXT,
    is_active INTEGER DEFAULT 1,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Pipeline Run Audit Table
CREATE TABLE IF NOT EXISTS pipeline_run_audit (
    run_id TEXT PRIMARY KEY,
    pipeline_id TEXT NOT NULL,
    status TEXT NOT NULL, -- SUCCESS, FAILED, PARTIAL
    records_extracted INTEGER DEFAULT 0,
    records_loaded INTEGER DEFAULT 0,
    records_rejected INTEGER DEFAULT 0,
    start_time TEXT NOT NULL,
    end_time TEXT,
    error_message TEXT,
    FOREIGN KEY (pipeline_id) REFERENCES pipeline_control(pipeline_id)
);

-- Data Quality Results Table
CREATE TABLE IF NOT EXISTS data_quality_results (
    dq_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    pipeline_id TEXT NOT NULL,
    check_name TEXT NOT NULL,
    check_type TEXT NOT NULL, -- schema, null, regex, min, duplicate
    status TEXT NOT NULL, -- PASSED, FAILED
    failed_count INTEGER DEFAULT 0,
    check_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Rejected Records / Quarantine Table
CREATE TABLE IF NOT EXISTS rejected_records (
    reject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    pipeline_id TEXT NOT NULL,
    raw_payload TEXT NOT NULL,
    reason_code TEXT NOT NULL, -- MISSING_PK, INVALID_EMAIL, SCHEMA_DRIFT, NEGATIVE_VALUE
    error_details TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- User Progress Table
CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week INTEGER NOT NULL,
    part INTEGER NOT NULL,
    lesson_id TEXT NOT NULL,
    status TEXT NOT NULL, -- COMPLETED, IN_PROGRESS, NOT_STARTED
    score REAL DEFAULT 0.0,
    attempts INTEGER DEFAULT 0,
    weak_topics TEXT,
    last_accessed TEXT DEFAULT CURRENT_TIMESTAMP
);
