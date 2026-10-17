import os
import pytest

def test_api_integration_flow(client):
    # 1. Health check
    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    # 2. Upload Excel file
    sample_file_path = "sample_data/sample_sales_data.xlsx"
    with open(sample_file_path, "rb") as f:
        upload_res = client.post(
            "/api/excel/upload",
            files={"file": ("sales_data.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    file_id = upload_data["file_id"]
    assert file_id > 0
    assert "SalesData" in upload_data["sheet_names"]

    # 3. Retrieve metadata
    meta_res = client.get(f"/api/excel/{file_id}/metadata")
    assert meta_res.status_code == 200
    meta_data = meta_res.json()
    assert "SalesData" in meta_data["sheets"]

    # 4. Ask: "What is the total sales amount?"
    q1_res = client.post("/api/chat/ask", json={
        "file_id": file_id,
        "question": "What is the total sales amount?"
    })
    assert q1_res.status_code == 200
    q1_data = q1_res.json()
    assert q1_data["analysis_result"] is not None
    assert q1_data["analysis_result"]["total"] > 0
    session_id = q1_data["session_id"]

    # 5. Ask: "Calculate the average sales for each region."
    q2_res = client.post("/api/chat/ask", json={
        "file_id": file_id,
        "session_id": session_id,
        "question": "Calculate the average sales for each region."
    })
    assert q2_res.status_code == 200
    q2_data = q2_res.json()
    assert q2_data["analysis_result"] is not None
    assert "rows" in q2_data["analysis_result"]

    # 6. Ask: "Give me an Excel formula to calculate profit margin."
    q3_res = client.post("/api/chat/ask", json={
        "file_id": file_id,
        "session_id": session_id,
        "question": "Give me an Excel formula to calculate profit margin."
    })
    assert q3_res.status_code == 200
    q3_data = q3_res.json()
    assert q3_data["formula"] is not None
    assert "IF" in q3_data["formula"]

    # 7. Ask: "Which product has the highest revenue?"
    q4_res = client.post("/api/chat/ask", json={
        "file_id": file_id,
        "session_id": session_id,
        "question": "Which product has the highest revenue?"
    })
    assert q4_res.status_code == 200
    assert q4_res.json()["analysis_result"] is not None

    # 8. Ask: "Create a bar chart comparing sales by region."
    q5_res = client.post("/api/chat/ask", json={
        "file_id": file_id,
        "session_id": session_id,
        "question": "Create a bar chart comparing sales by region."
    })
    assert q5_res.status_code == 200
    q5_data = q5_res.json()
    assert q5_data["chart_url"] is not None
    assert q5_data["chart_type"] == "bar"

    # 9. Ask: "Show monthly sales as a line chart."
    q6_res = client.post("/api/chat/ask", json={
        "file_id": file_id,
        "session_id": session_id,
        "question": "Show monthly sales as a line chart."
    })
    assert q6_res.status_code == 200
    q6_data = q6_res.json()
    assert q6_data["chart_url"] is not None
    assert q6_data["chart_type"] == "line"

    # 10. Ask: "Find the top 10 customers by total purchase amount."
    q7_res = client.post("/api/chat/ask", json={
        "file_id": file_id,
        "session_id": session_id,
        "question": "Find the top 10 customers by total purchase amount."
    })
    assert q7_res.status_code == 200
    assert len(q7_res.json()["analysis_result"]["rows"]) <= 10

    # 11. Ask: "Add a formula to calculate the difference between Actual and Target."
    q8_res = client.post("/api/chat/ask", json={
        "file_id": file_id,
        "session_id": session_id,
        "question": "Add a formula to calculate the difference between Actual and Target.",
        "modify_excel": True
    })
    assert q8_res.status_code == 200
    q8_data = q8_res.json()
    assert q8_data["formula"] is not None
    assert "-" in q8_data["formula"]
    assert q8_data["modified_file_url"] is not None

    # 12. Download modified file
    mod_dl_res = client.get(f"/api/excel/{file_id}/download-modified")
    assert mod_dl_res.status_code == 200

    # 13. Verify Analysis History persistence in SQL
    history_res = client.get("/api/history")
    assert history_res.status_code == 200
    history_records = history_res.json()
    assert len(history_records) >= 8
