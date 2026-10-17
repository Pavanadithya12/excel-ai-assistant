import os
import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.excel_file import ExcelFile
from app.models.user import User
from app.schemas.excel import ExcelUploadResponse, ExcelMetadataResponse
from app.services.auth_service import get_optional_current_user, get_current_user
from app.services.excel_service import excel_service

router = APIRouter(prefix="/api/excel", tags=["Spreadsheet & Metadata"])

@router.post("/upload", response_model=ExcelUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_excel_file(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an Excel (.xlsx, .xls) or CSV file.
    Parses worksheets, columns, headers, inferred data types, and spreadsheet metadata.
    """
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".xlsx", ".xls", ".csv"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload an Excel (.xlsx, .xls) or .csv file."
        )

    # Save to uploads directory with unique stored name
    unique_name = f"{uuid.uuid4().hex[:12]}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    content = await file.read()
    file_size = len(content)

    with open(file_path, "wb") as f:
        f.write(content)

    # Inspect metadata using pandas & openpyxl
    try:
        inspection = excel_service.inspect_file(file_path)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Failed to inspect spreadsheet: {str(e)}")

    sheet_names_list = inspection["sheet_names"]

    # Store in database
    excel_record = ExcelFile(
        user_id=current_user.id if current_user else None,
        filename=filename,
        stored_filename=unique_name,
        filepath=file_path,
        file_size=file_size,
        sheet_names=json.dumps(sheet_names_list),
        metadata_json=json.dumps(inspection)
    )
    db.add(excel_record)
    db.commit()
    db.refresh(excel_record)

    metadata_resp = ExcelMetadataResponse(
        file_id=excel_record.id,
        filename=excel_record.filename,
        file_size=excel_record.file_size,
        sheet_names=sheet_names_list,
        sheets=inspection["sheets"],
        created_at=excel_record.created_at
    )

    return {
        "file_id": excel_record.id,
        "filename": excel_record.filename,
        "file_size": excel_record.file_size,
        "sheet_names": sheet_names_list,
        "metadata": metadata_resp,
        "message": f"Successfully analyzed {len(sheet_names_list)} sheet(s) and {sum(s['column_count'] for s in inspection['sheets'].values())} column(s)."
    }

@router.post("/load-sample", response_model=ExcelUploadResponse)
def load_sample_file(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Loads or creates the sample sales dataset directly on the server"""
    sample_path = os.path.abspath("sample_data/sample_sales_data.xlsx")
    if not os.path.exists(sample_path):
        from sample_data.create_sample_excel import generate_sample_sales_data
        generate_sample_sales_data(sample_path)

    # Check if already in db
    existing = db.query(ExcelFile).filter(ExcelFile.filename == "sample_sales_data.xlsx").first()
    if existing and os.path.exists(existing.filepath):
        inspection = json.loads(existing.metadata_json)
        sheet_names_list = json.loads(existing.sheet_names)
        metadata_resp = ExcelMetadataResponse(
            file_id=existing.id,
            filename=existing.filename,
            file_size=existing.file_size,
            sheet_names=sheet_names_list,
            sheets=inspection["sheets"],
            created_at=existing.created_at
        )
        return {
            "file_id": existing.id,
            "filename": existing.filename,
            "file_size": existing.file_size,
            "sheet_names": sheet_names_list,
            "metadata": metadata_resp,
            "message": "Sample sales dataset loaded successfully."
        }

    inspection = excel_service.inspect_file(sample_path)
    sheet_names_list = inspection["sheet_names"]
    file_size = os.path.getsize(sample_path)

    excel_record = ExcelFile(
        user_id=current_user.id if current_user else None,
        filename="sample_sales_data.xlsx",
        stored_filename="sample_sales_data.xlsx",
        filepath=sample_path,
        file_size=file_size,
        sheet_names=json.dumps(sheet_names_list),
        metadata_json=json.dumps(inspection)
    )
    db.add(excel_record)
    db.commit()
    db.refresh(excel_record)

    metadata_resp = ExcelMetadataResponse(
        file_id=excel_record.id,
        filename=excel_record.filename,
        file_size=excel_record.file_size,
        sheet_names=sheet_names_list,
        sheets=inspection["sheets"],
        created_at=excel_record.created_at
    )
    return {
        "file_id": excel_record.id,
        "filename": excel_record.filename,
        "file_size": excel_record.file_size,
        "sheet_names": sheet_names_list,
        "metadata": metadata_resp,
        "message": "Sample sales dataset loaded successfully."
    }

@router.get("/files", response_model=List[dict])
def list_uploaded_files(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Lists files uploaded by current user or recent files"""
    query = db.query(ExcelFile)
    if current_user:
        query = query.filter((ExcelFile.user_id == current_user.id) | (ExcelFile.user_id == None))
    files = query.order_by(ExcelFile.id.desc()).limit(20).all()
    
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "file_size": f.file_size,
            "sheet_names": json.loads(f.sheet_names) if f.sheet_names else [],
            "created_at": f.created_at,
            "has_modified_version": bool(f.modified_filepath and os.path.exists(f.modified_filepath))
        }
        for f in files
    ]

@router.get("/{file_id}/metadata", response_model=ExcelMetadataResponse)
def get_file_metadata(file_id: int, db: Session = Depends(get_db)):
    """Retrieves full worksheet structure and column statistics for a file"""
    file_record = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="Excel file not found.")

    inspection = json.loads(file_record.metadata_json) if file_record.metadata_json else {}
    sheet_names = json.loads(file_record.sheet_names) if file_record.sheet_names else []

    return ExcelMetadataResponse(
        file_id=file_record.id,
        filename=file_record.filename,
        file_size=file_record.file_size,
        sheet_names=sheet_names,
        sheets=inspection.get("sheets", {}),
        created_at=file_record.created_at
    )

@router.get("/{file_id}/download")
def download_original_file(file_id: int, db: Session = Depends(get_db)):
    """Downloads the original uploaded Excel file"""
    file_record = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
    if not file_record or not os.path.exists(file_record.filepath):
        raise HTTPException(status_code=404, detail="File not found on server.")
    return FileResponse(
        file_record.filepath,
        filename=file_record.filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/{file_id}/download-modified")
def download_modified_file(file_id: int, db: Session = Depends(get_db)):
    """Downloads the AI-modified workbook containing injected formulas, summaries, and charts"""
    file_record = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File record not found.")
    
    # If no modified file exists yet, generate one on demand
    target_path = file_record.modified_filepath
    if not target_path or not os.path.exists(target_path):
        mod_filename = f"ai_enhanced_{file_record.filename}"
        target_path = os.path.join(settings.UPLOAD_DIR, f"mod_{file_record.stored_filename}")
        excel_service.create_modified_workbook(
            filepath=file_record.filepath,
            output_path=target_path
        )
        file_record.modified_filepath = target_path
        db.commit()

    return FileResponse(
        target_path,
        filename=f"ai_enhanced_{file_record.filename}",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
