from typing import Optional
from pydantic import BaseModel

class FormulaGenerateRequest(BaseModel):
    file_id: int
    sheet_name: Optional[str] = None
    prompt: str

class FormulaGenerateResponse(BaseModel):
    formula: str
    explanation: str
    target_range: Optional[str] = None
    example_usage: Optional[str] = None
    syntax_valid: bool = True

class FormulaValidateRequest(BaseModel):
    formula: str

class FormulaValidateResponse(BaseModel):
    formula: str
    is_valid: bool
    function_name: Optional[str] = None
    message: str
