from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    file_id = Column(Integer, ForeignKey("excel_files.id"), nullable=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True, index=True)
    question = Column(Text, nullable=False)
    operation_type = Column(String(50), nullable=False)  # formula, summary, chart, query, web_research
    sheet_name = Column(String(100), nullable=True)
    formula_generated = Column(Text, nullable=True)
    summary_result = Column(Text, nullable=True)  # JSON or text summary
    chart_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="analysis_history")
    file = relationship("ExcelFile", back_populates="analysis_history")
