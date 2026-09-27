"""
Week 3 Hands-on Lab Solution: Production Pipeline Patterns & DLQ Routing
Reference solution for Week 3 exercises.
"""
from typing import List, Dict, Tuple, Any

def process_and_route_dlq(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Inspect records and isolate corrupted rows into DLQ."""
    valid_records = []
    dlq_records = []
    
    for r in records:
        errors = []
        if r.get("amount", 0) < 0:
            errors.append("ERR_NEG_AMOUNT: Amount must be non-negative")
        email = r.get("email")
        if not email or "@" not in str(email):
            errors.append("ERR_INVALID_EMAIL: Email missing @ domain")
            
        if errors:
            dlq_records.append({
                "payload": r,
                "error_code": "DATA_QUALITY_FAILURE",
                "error_reasons": "; ".join(errors)
            })
        else:
            valid_records.append(r)
            
    return valid_records, dlq_records
