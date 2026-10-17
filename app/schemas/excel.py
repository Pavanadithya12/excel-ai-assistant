from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ColumnMetadata(BaseModel):
    name: str
    column_letter: str
    data_type: str  # numeric, text, datetime, boolean
    non_null_count: int
    null_count: int
    sample_values: List[Any] = []
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None
    mean_val: Optional[float] = None

class SheetMetadata(BaseModel):
    sheet_name: str
    row_count: int
    column_count: int
    columns: List[ColumnMetadata]
    preview_rows: List[Dict[str, Any]]

class ExcelMetadataResponse(BaseModel):
    file_id: int
    filename: str
    file_size: int
    sheet_names: List[str]
    sheets: Dict[str, SheetMetadata]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ExcelUploadResponse(BaseModel):
    file_id: int
    filename: str
    file_size: int
    sheet_names: List[str]
    metadata: ExcelMetadataResponse
    message: str = "Excel file uploaded and analyzed successfully"
