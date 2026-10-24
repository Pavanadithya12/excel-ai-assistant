import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.excel_file import ExcelFile
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    QuestionRequest, ChatMessageResponse, ChatSessionCreate, ChatSessionResponse, ChatSessionListItem
)
from app.services.auth_service import get_optional_current_user
from app.services.chat_service import chat_service

router = APIRouter(prefix="/api/chat", tags=["Chat & AI Spreadsheet Assistant"])

@router.post("/ask", response_model=ChatMessageResponse)
def ask_spreadsheet_question(
    request: QuestionRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Main Assistant Endpoint:
    Ask natural-language questions about an uploaded spreadsheet.
    Interprets intent via LLM, creates Excel formulas, executes Pandas analyses,
    generates charts, and persists history in SQL.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        response_data = chat_service.process_user_query(
            db=db,
            user=current_user,
            question=request.question.strip(),
            file_id=request.file_id,
            session_id=request.session_id,
            sheet_name=request.sheet_name,
            enable_web_research=request.enable_web_research,
            modify_excel=request.modify_excel
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

    return ChatMessageResponse(
        id=response_data["message_id"],
        session_id=response_data["session_id"],
        role="assistant",
        content=response_data["content"],
        query_type=response_data["query_type"],
        formula=response_data["formula"],
        formula_explanation=response_data["formula_explanation"],
        analysis_result=response_data["analysis_result"],
        chart_url=response_data["chart_url"],
        chart_type=response_data["chart_type"],
        modified_file_url=response_data["modified_file_url"],
        created_at=response_data["created_at"]
    )

@router.get("/sessions", response_model=List[ChatSessionListItem])
def list_chat_sessions(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Lists chat sessions with message counts"""
    query = db.query(ChatSession)
    if current_user:
        query = query.filter((ChatSession.user_id == current_user.id) | (ChatSession.user_id == None))
    sessions = query.order_by(ChatSession.updated_at.desc()).limit(30).all()

    result = []
    for s in sessions:
        file_name = s.file.filename if s.file else None
        msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).count()
        result.append(ChatSessionListItem(
            id=s.id,
            file_id=s.file_id,
            filename=file_name,
            title=s.title,
            message_count=msg_count,
            updated_at=s.updated_at
        ))
    return result

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Retrieves full conversation transcript and artifacts for a chat session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.id.asc()).all()

    formatted_messages = []
    for m in messages:
        analysis_dict = json.loads(m.analysis_result) if m.analysis_result else None
        formatted_messages.append(ChatMessageResponse(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            query_type=m.query_type,
            formula=m.formula,
            formula_explanation=m.formula_explanation,
            analysis_result=analysis_dict,
            chart_url=m.chart_url,
            chart_type=m.chart_type,
            modified_file_url=m.modified_file_url,
            created_at=m.created_at
        ))

    return ChatSessionResponse(
        id=session.id,
        user_id=session.user_id,
        file_id=session.file_id,
        filename=session.file.filename if session.file else None,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=formatted_messages
    )

@router.delete("/sessions/{session_id}")
def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Deletes a chat session and its messages safely"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()
    return {"message": "Chat session deleted successfully.", "session_id": session_id}
