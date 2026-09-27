"""
Week 3 Hands-on Lab Starter: Production Pipeline Patterns & DLQ Routing
Instructions: Fill in the TODO sections to route corrupted records to Dead Letter Queue (DLQ).
"""

def process_and_route_dlq(records):
    """
    TODO 1: Inspect incoming records.
    If 'amount' is negative or 'email' is invalid (missing @), append to dlq_records with error_code and reason.
    Otherwise, append to valid_records.
    """
    valid_records = []
    dlq_records = []
    
    # TODO: Implement validation and DLQ routing logic
    return valid_records, dlq_records
