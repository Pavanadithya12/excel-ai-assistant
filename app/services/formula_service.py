import re
from typing import Dict, Any, Optional

class FormulaService:
    KNOWN_EXCEL_FUNCTIONS = {
        "SUM", "AVERAGE", "COUNT", "COUNTA", "COUNTIF", "COUNTIFS",
        "SUMIF", "SUMIFS", "AVERAGEIF", "AVERAGEIFS",
        "MIN", "MAX", "MEDIAN", "STDEV", "STDEV.S", "STDEV.P",
        "VLOOKUP", "HLOOKUP", "XLOOKUP", "LOOKUP", "INDEX", "MATCH",
        "IF", "IFS", "IFERROR", "IFNA", "AND", "OR", "NOT",
        "CONCAT", "CONCATENATE", "TEXT", "LEFT", "RIGHT", "MID", "LEN",
        "TRIM", "UPPER", "LOWER", "PROPER",
        "ROUND", "ROUNDUP", "ROUNDDOWN", "ABS", "POWER", "SQRT",
        "TODAY", "NOW", "DATE", "YEAR", "MONTH", "DAY", "DATEDIF"
    }

    @staticmethod
    def validate_formula(formula: str) -> Dict[str, Any]:
        """
        Validates the syntax of an Excel formula string:
        - Must begin with '='
        - Balanced parentheses ()
        - Balanced quotes ""
        - Identifies the primary function name
        """
        if not formula or not isinstance(formula, str):
            return {
                "is_valid": False,
                "formula": formula or "",
                "function_name": None,
                "message": "Formula cannot be empty."
            }

        clean_formula = formula.strip()
        if not clean_formula.startswith("="):
            clean_formula = "=" + clean_formula

        # Check balanced quotes
        in_quotes = False
        paren_stack = 0
        for char in clean_formula:
            if char == '"':
                in_quotes = not in_quotes
            elif not in_quotes:
                if char == '(':
                    paren_stack += 1
                elif char == ')':
                    paren_stack -= 1
                    if paren_stack < 0:
                        return {
                            "is_valid": False,
                            "formula": clean_formula,
                            "function_name": None,
                            "message": "Syntax Error: Unmatched closing parenthesis ')'."
                        }

        if in_quotes:
            return {
                "is_valid": False,
                "formula": clean_formula,
                "function_name": None,
                "message": "Syntax Error: Unclosed double quotation mark."
            }

        if paren_stack != 0:
            return {
                "is_valid": False,
                "formula": clean_formula,
                "function_name": None,
                "message": f"Syntax Error: {paren_stack} unclosed opening parenthesis '('."
            }

        # Extract primary function if any
        func_match = re.search(r"=\s*([A-Za-z0-9_\.]+)\s*\(", clean_formula)
        func_name = None
        if func_match:
            detected = func_match.group(1).upper()
            func_name = detected
            if detected not in FormulaService.KNOWN_EXCEL_FUNCTIONS:
                # May still be valid arithmetic or custom, but note it
                pass

        return {
            "is_valid": True,
            "formula": clean_formula,
            "function_name": func_name,
            "message": "Formula syntax is valid."
        }

    @staticmethod
    def build_formula(
        operation: str,
        target_col_letter: str,
        start_row: int = 2,
        end_row: int = 100,
        criteria_col_letter: Optional[str] = None,
        criteria_value: Optional[str] = None,
        secondary_col_letter: Optional[str] = None,
        row_ref: int = 2
    ) -> Dict[str, str]:
        """
        Builds standard formulas based on parameters and returns formula + explanation.
        """
        op = operation.lower().strip()
        
        if op == "sum":
            formula = f"=SUM({target_col_letter}{start_row}:{target_col_letter}{end_row})"
            explanation = f"Calculates the total sum of cells {target_col_letter}{start_row} through {target_col_letter}{end_row}."
        elif op == "average":
            formula = f"=AVERAGE({target_col_letter}{start_row}:{target_col_letter}{end_row})"
            explanation = f"Computes the arithmetic mean of cells {target_col_letter}{start_row} through {target_col_letter}{end_row}."
        elif op == "sumif" and criteria_col_letter and criteria_value:
            formula = f'=SUMIF({criteria_col_letter}{start_row}:{criteria_col_letter}{end_row}, "{criteria_value}", {target_col_letter}{start_row}:{target_col_letter}{end_row})'
            explanation = f'Sums values in column {target_col_letter} where column {criteria_col_letter} equals "{criteria_value}".'
        elif op == "countif" and target_col_letter and criteria_value:
            formula = f'=COUNTIF({target_col_letter}{start_row}:{target_col_letter}{end_row}, "{criteria_value}")'
            explanation = f'Counts the number of cells in {target_col_letter}{start_row}:{target_col_letter}{end_row} that equal "{criteria_value}".'
        elif op == "profit_margin" and secondary_col_letter:
            # Profit Margin = Profit / Revenue = (Revenue - Cost) / Revenue
            # target_col = Profit (or ActualSales), secondary = ActualSales
            formula = f'=IF({secondary_col_letter}{row_ref}>0, {target_col_letter}{row_ref}/{secondary_col_letter}{row_ref}, 0)'
            explanation = f"Calculates profit margin as a percentage: ({target_col_letter}{row_ref} / {secondary_col_letter}{row_ref}), with division-by-zero protection."
        elif op == "difference" and secondary_col_letter:
            # Difference = Actual - Target
            formula = f'={target_col_letter}{row_ref}-{secondary_col_letter}{row_ref}'
            explanation = f"Calculates the variance or difference ({target_col_letter}{row_ref} minus {secondary_col_letter}{row_ref})."
        elif op == "xlookup" and criteria_col_letter and secondary_col_letter:
            formula = f'=XLOOKUP({criteria_col_letter}{row_ref}, RegionalTargets!$A$2:$A$5, {secondary_col_letter}, "N/A")'
            explanation = f"Performs modern exact-match lookup on key {criteria_col_letter}{row_ref}."
        elif op == "vlookup" and criteria_col_letter:
            formula = f'=VLOOKUP({criteria_col_letter}{row_ref}, RegionalTargets!$A$2:$D$5, 2, FALSE)'
            explanation = f"Searches the lookup table for the value in {criteria_col_letter}{row_ref} and returns column 2."
        elif op == "if_target":
            formula = f'=IF({target_col_letter}{row_ref}>={secondary_col_letter}{row_ref}, "Met Target", "Below Target")'
            explanation = f"Evaluates whether Actual ({target_col_letter}{row_ref}) is greater than or equal to Target ({secondary_col_letter}{row_ref})."
        else:
            formula = f"=SUM({target_col_letter}{start_row}:{target_col_letter}{end_row})"
            explanation = f"Formula for {target_col_letter}."

        return {
            "formula": formula,
            "explanation": explanation
        }

formula_service = FormulaService()
