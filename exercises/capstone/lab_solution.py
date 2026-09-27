"""
Capstone Hands-on Lab Solution: Flipkart Order Analytics Platform
Reference solution for Capstone exercises.
"""
from typing import Dict, Any
from src.capstone.flipkart_analytics import run_capstone_pipeline

def integrate_flipkart_multi_source(step: str = "all") -> Dict[str, Any]:
    """Execute complete Flipkart 6-source order analytics platform."""
    return run_capstone_pipeline(step=step)
