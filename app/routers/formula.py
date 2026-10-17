import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.excel_file import ExcelFile
from app.schemas.formula import (
    FormulaGenerateRequest, FormulaGenerateResponse,
    FormulaValidateRequest, FormulaValidateResponse
)
from app.services.formula_service import formula_service
from app.services.llm_service import llm_service

router = APIRouter(prefix="/api/formula", tags=["Excel Formulas"])

@router.post("/generate", response_model=FormulaGenerateResponse)
def generate_formula(request: FormulaGenerateRequest, db: Session = Depends(get_db)):
    """
    Generates a syntactically correct Excel formula (SUM, AVERAGE, IF, SUMIF, COUNTIF,
    XLOOKUP, VLOOKUP, difference, profit margin, etc.) mapped to spreadsheet columns.
    """
    file_record = db.query(ExcelFile).filter(ExcelFile.id == request.file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="Excel file not found.")

    metadata = json.loads(file_record.metadata_json) if file_record.metadata_json else {}
    plan = llm_service.interpret_question(request.prompt, metadata, request.sheet_name)

    f_info = plan.get("formula")
    if not f_info or not f_info.get("formula_string"):
        # Default fallback formula
        formula_str = "=SUM(A2:A100)"
        explanation = "Generic summation formula."
    else:
        formula_str = f_info.get("formula_string")
        explanation = f_info.get("explanation", "Generated formula.")

    # Validate syntax
    val_res = formula_service.validate_formula(formula_str)

    return FormulaGenerateResponse(
        formula=formula_str,
        explanation=explanation,
        target_range=f_info.get("target_column") if f_info else None,
        example_usage=formula_str,
        syntax_valid=val_res["is_valid"]
    )

@router.post("/validate", response_model=FormulaValidateResponse)
def validate_formula_syntax(request: FormulaValidateRequest):
    """
    Validates formula syntax, balanced parentheses, and recognized functions.
    """
    res = formula_service.validate_formula(request.formula)
    return FormulaValidateResponse(
        formula=res["formula"],
        is_valid=res["is_valid"],
        function_name=res["function_name"],
        message=res["message"]
    )
