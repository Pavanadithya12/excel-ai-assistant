import pytest
import pandas as pd
from app.services.analysis_service import analysis_service

@pytest.fixture
def sample_df():
    return pd.DataFrame([
        {"Region": "North", "Product": "Laptop", "Sales": 1000.0, "Target": 900.0},
        {"Region": "North", "Product": "Mouse", "Sales": 200.0, "Target": 250.0},
        {"Region": "South", "Product": "Laptop", "Sales": 1500.0, "Target": 1400.0},
        {"Region": "East", "Product": "Keyboard", "Sales": 300.0, "Target": 300.0},
        {"Region": "West", "Product": "Monitor", "Sales": 800.0, "Target": 750.0},
    ])

def test_calculate_total_or_metric(sample_df):
    total_res = analysis_service.calculate_total_or_metric(sample_df, "Sales", metric="sum")
    assert total_res["value"] == 3800.0
    assert total_res["count"] == 5

    avg_res = analysis_service.calculate_total_or_metric(sample_df, "Sales", metric="average")
    assert avg_res["value"] == 760.0

def test_group_by_and_aggregate(sample_df):
    grp_res = analysis_service.group_by_and_aggregate(sample_df, "Region", "Sales", agg_func="sum")
    assert len(grp_res["rows"]) == 4
    # South should be highest (1500)
    assert grp_res["rows"][0]["Region"] == "South"
    assert grp_res["rows"][0]["Sales"] == 1500.0

def test_get_top_n(sample_df):
    top_res = analysis_service.get_top_n(sample_df, "Product", "Sales", n=2)
    assert len(top_res["rows"]) == 2
    assert top_res["rows"][0]["Product"] == "Laptop"

def test_calculate_column_difference(sample_df):
    diff_res = analysis_service.calculate_column_difference(sample_df, "Sales", "Target")
    # Total Sales: 3800, Total Target: 3600 -> Diff: 200
    assert diff_res["total_difference"] == 200.0
    assert diff_res["positive_count"] == 3
