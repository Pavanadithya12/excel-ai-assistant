from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class QuestionRequest(BaseModel):
    file_id: Optional[int] = None
    session_id: Optional[int] = None
    sheet_name: Optional[str] = None
    question: str
    enable_web_research: bool = False
    modify_excel: bool = False

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    query_type: Optional[str] = None
    formula: Optional[str] = None
    formula_explanation: Optional[str] = None
    analysis_result: Optional[Dict[str, Any]] = None
    chart_url: Optional[str] = None
    chart_type: Optional[str] = None
    modified_file_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatSessionCreate(BaseModel):
    file_id: Optional[int] = None
    title: Optional[str] = "New Chat"

class ChatSessionListItem(BaseModel):
    id: int
    file_id: Optional[int] = None
    filename: Optional[str] = None
    title: str
    message_count: int = 0
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatSessionResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    file_id: Optional[int] = None
    filename: Optional[str] = None
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)
