"""
Week 4 Hands-on Lab Solution: Metadata Orchestration & PII Anonymization
Reference solution for Week 4 exercises.
"""
import hashlib
from typing import Dict, Any

def mask_pii_fields(record: Dict[str, Any], pepper: str = "DE_LEARNING_PEPPER_2026") -> Dict[str, Any]:
    """Mask PII fields and generate deterministic pseudonym token."""
    res = record.copy()
    
    # Email masking
    email = str(res.get("email", ""))
    if "@" in email:
        user, domain = email.split("@", 1)
        res["email"] = f"{user[:2]}***@{domain}"
    else:
        res["email"] = "***@masked.com"
        
    # Phone masking
    phone = str(res.get("phone", ""))
    if len(phone) >= 10:
        res["phone"] = f"+91XXXXXX{phone[-4:]}"
    else:
        res["phone"] = "+91XXXXXXXXXX"
        
    # SHA-256 Tokenization
    cid = str(res.get("customer_id", ""))
    res["customer_token"] = hashlib.sha256(f"{cid}_{pepper}".encode("utf-8")).hexdigest()
    
    return res
