import pytest
from app.services.formula_service import formula_service

def test_formula_validation_valid():
    valid_cases = [
        "=SUM(A1:A10)",
        "=AVERAGE(B2:B50)",
        '=IF(C2>0, (C2-D2)/C2, 0)',
        '=COUNTIF(D2:D100, "North")',
        '=SUMIF(Region2:Region100, "East", Sales2:Sales100)',
        '=XLOOKUP(A2, Target!A2:A10, Target!B2:B10, "Not Found")'
    ]
    for f in valid_cases:
        res = formula_service.validate_formula(f)
        assert res["is_valid"] is True, f"Failed on valid formula: {f}"

def test_formula_validation_invalid():
    # Unmatched parenthesis
    res1 = formula_service.validate_formula("=SUM(A1:A10")
    assert res1["is_valid"] is False
    assert "unclosed" in res1["message"].lower()

    # Unmatched quote
    res2 = formula_service.validate_formula('=COUNTIF(A1:A10, "North)')
    assert res2["is_valid"] is False

    # Extra closing parenthesis
    res3 = formula_service.validate_formula("=AVERAGE(B1:B10))")
    assert res3["is_valid"] is False

def test_formula_building():
    # Profit Margin
    f_res = formula_service.build_formula(
        operation="profit_margin",
        target_col_letter="M",  # Profit
        secondary_col_letter="J",  # ActualSales
        row_ref=2
    )
    assert f_res["formula"] == "=IF(J2>0, M2/J2, 0)"

    # Difference
    diff_res = formula_service.build_formula(
        operation="difference",
        target_col_letter="J",
        secondary_col_letter="K",
        row_ref=2
    )
    assert diff_res["formula"] == "=J2-K2"
