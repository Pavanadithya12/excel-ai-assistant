from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.history import AnalysisHistory
from app.services.auth_service import get_optional_current_user

router = APIRouter(prefix="/api/history", tags=["Analysis History"])

@router.get("", response_model=List[dict])
def get_analysis_history(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns SQL-persisted analysis history including questions asked,
    formulas generated, data summaries, and chart URLs.
    """
    query = db.query(AnalysisHistory)
    if current_user:
        query = query.filter((AnalysisHistory.user_id == current_user.id) | (AnalysisHistory.user_id == None))
    records = query.order_by(AnalysisHistory.id.desc()).limit(50).all()

    return [
        {
            "id": r.id,
            "file_id": r.file_id,
            "filename": r.file.filename if r.file else None,
            "session_id": r.session_id,
            "question": r.question,
            "operation_type": r.operation_type,
            "sheet_name": r.sheet_name,
            "formula_generated": r.formula_generated,
            "summary_result": r.summary_result,
            "chart_path": r.chart_path,
            "created_at": r.created_at
        }
        for r in records
    ]

@router.get("/{history_id}", response_model=dict)
def get_history_detail(history_id: int, db: Session = Depends(get_db)):
    """Retrieves a single analysis history record"""
    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis history record not found.")

    return {
        "id": record.id,
        "file_id": record.file_id,
        "filename": record.file.filename if record.file else None,
        "session_id": record.session_id,
        "question": record.question,
        "operation_type": record.operation_type,
        "sheet_name": record.sheet_name,
        "formula_generated": record.formula_generated,
        "summary_result": record.summary_result,
        "chart_path": record.chart_path,
        "created_at": record.created_at
    }

@router.delete("", response_model=dict)
def clear_all_history(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Clears all analysis history records for current user from database"""
    query = db.query(AnalysisHistory)
    if current_user:
        query = query.filter((AnalysisHistory.user_id == current_user.id) | (AnalysisHistory.user_id == None))
    deleted_count = query.delete(synchronize_session=False)
    db.commit()
    return {"message": f"Cleared {deleted_count} analysis record(s)."}

@router.delete("/{history_id}")
def delete_history_record(history_id: int, db: Session = Depends(get_db)):
    """Deletes an analysis history item"""
    record = db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis history record not found.")
    db.delete(record)
    db.commit()
    return {"message": "History item deleted."}
