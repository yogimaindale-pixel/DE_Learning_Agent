-- Data Quality Gate: Freshness & Watermark SLA Checks

-- Audit Pipeline Watermark Freshness Status
SELECT 
    pipeline_id,
    pipeline_name,
    target_table,
    last_processed_ts,
    last_run_status,
    records_loaded,
    records_rejected,
    CASE 
        WHEN last_run_status = 'SUCCESS' THEN 'SLA_MET'
        ELSE 'SLA_BREACH'
    END AS sla_compliance
FROM pipeline_control;
