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

def test_column_resolution_with_whitespace():
    df_spaces = pd.DataFrame([
        {"  Name  ": "Alice", " Sales ": 100},
        {"  Name  ": "Bob", " Sales ": 200}
    ])
    res = analysis_service.calculate_total_or_metric(df_spaces, "Sales", metric="sum")
    assert res["value"] == 300.0

    grp = analysis_service.group_by_and_aggregate(df_spaces, "name", "sales", agg_func="sum")
    assert len(grp["rows"]) == 2

def test_summary_intent_with_text_only_columns():
    from app.services.llm_service import llm_service
    metadata = {
        "sheet_names": ["Tasks"],
        "sheets": {
            "Tasks": {
                "row_count": 46,
                "column_count": 5,
                "columns": [
                    {"name": "Project Name", "column_letter": "A", "data_type": "text", "null_count": 0},
                    {"name": "Task Name", "column_letter": "B", "data_type": "text", "null_count": 0},
                    {"name": "Assigned to", "column_letter": "C", "data_type": "text", "null_count": 2},
                    {"name": "Start Date", "column_letter": "D", "data_type": "text", "null_count": 0},
                    {"name": "Days Required", "column_letter": "E", "data_type": "text", "null_count": 0}
                ]
            }
        }
    }
    # This previously crashed with: 'NoneType' object is not subscriptable
    res = llm_service.interpret_question("Summarize key column distributions and null values.", metadata, "Tasks")
    assert res["query_type"] == "general"
    assert "Spreadsheet Overview" in res["explanation"]
    assert "46" in res["explanation"]

    res_count = llm_service.interpret_question("how many data is there", metadata, "Tasks")
    assert res_count["query_type"] == "general"
    assert "46" in res_count["explanation"]
