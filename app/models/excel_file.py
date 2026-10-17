from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ExcelFile(Base):
    __tablename__ = "excel_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    sheet_names = Column(Text, nullable=False)  # JSON-encoded list of sheet names
    metadata_json = Column(Text, nullable=True)  # Detailed sheet columns, data types, statistics, preview rows
    modified_filepath = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="excel_files")
    chat_sessions = relationship("ChatSession", back_populates="file", cascade="all, delete-orphan")
    analysis_history = relationship("AnalysisHistory", back_populates="file", cascade="all, delete-orphan")
