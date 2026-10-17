import os
import pytest
import pandas as pd
from app.services.chart_service import chart_service

@pytest.fixture
def chart_test_df():
    return pd.DataFrame([
        {"Region": "North", "Sales": 12000, "Units": 30},
        {"Region": "South", "Sales": 18000, "Units": 45},
        {"Region": "East", "Sales": 15000, "Units": 35},
        {"Region": "West", "Sales": 9000, "Units": 20},
    ])

def test_generate_bar_chart(chart_test_df):
    res = chart_service.generate_chart(chart_test_df, "bar", "Region", "Sales", "Sales by Region")
    assert os.path.exists(res["filepath"])
    assert res["url"].startswith("/static/charts/")
    assert res["base64_uri"].startswith("data:image/png;base64,")

def test_generate_line_chart(chart_test_df):
    res = chart_service.generate_chart(chart_test_df, "line", "Region", "Sales", "Sales Trend")
    assert os.path.exists(res["filepath"])
    assert res["chart_type"] == "line"

def test_generate_pie_chart(chart_test_df):
    res = chart_service.generate_chart(chart_test_df, "pie", "Region", "Sales", "Sales Share")
    assert os.path.exists(res["filepath"])
    assert res["chart_type"] == "pie"

def test_generate_scatter_chart(chart_test_df):
    res = chart_service.generate_chart(chart_test_df, "scatter", "Units", "Sales", "Units vs Sales")
    assert os.path.exists(res["filepath"])
    assert res["chart_type"] == "scatter"
