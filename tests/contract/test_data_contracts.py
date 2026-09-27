import pytest
import pandera as pa
import pandas as pd
from src.week3.part2_testing_monitoring import demo_pandera_contract_testing

def test_pandera_schema_contract():
    res = demo_pandera_contract_testing()
    assert res["validation_passed"] is True
    assert res["validated_rows"] > 0
