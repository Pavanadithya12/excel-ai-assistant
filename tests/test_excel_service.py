import os
import pytest
import pandas as pd
from app.services.excel_service import excel_service

def test_inspect_sample_excel():
    filepath = "sample_data/sample_sales_data.xlsx"
    assert os.path.exists(filepath), "Sample file must exist"

    inspection = excel_service.inspect_file(filepath)
    assert "sheet_names" in inspection
    assert "SalesData" in inspection["sheet_names"]
    assert "RegionalTargets" in inspection["sheet_names"]

    sales_sheet = inspection["sheets"]["SalesData"]
    assert sales_sheet["row_count"] == 100
    assert sales_sheet["column_count"] >= 10

    # Verify column metadata extraction
    col_names = [c["name"] for c in sales_sheet["columns"]]
    assert "Region" in col_names
    assert "ActualSales" in col_names
    assert "TargetSales" in col_names
    assert "Profit" in col_names

    # Check numeric statistics
    sales_col = next(c for c in sales_sheet["columns"] if c["name"] == "ActualSales")
    assert sales_col["data_type"] == "numeric"
    assert sales_col["mean_val"] is not None
    assert sales_col["min_val"] > 0

def test_create_modified_workbook(tmp_path):
    orig_path = "sample_data/sample_sales_data.xlsx"
    out_path = str(tmp_path / "modified_sales.xlsx")

    summary_df = pd.DataFrame([
        {"Region": "North", "TotalSales": 125000.0},
        {"Region": "South", "TotalSales": 98000.0}
    ])

    result_path = excel_service.create_modified_workbook(
        filepath=orig_path,
        output_path=out_path,
        sheet_name="SalesData",
        new_column_header="Variance_Actual_Target",
        formula_template="=J{row}-K{row}",
        summary_table=summary_df
    )

    assert os.path.exists(result_path)
    # Check that modified sheet contains AI_Analysis_Summary
    excel_file = pd.ExcelFile(result_path, engine="openpyxl")
    assert "AI_Analysis_Summary" in excel_file.sheet_names
