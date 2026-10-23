import os
import json
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class ExcelService:
    @staticmethod
    def detect_file_type(filepath: str) -> str:
        """Identifies human-readable document type from file extension"""
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".xlsx":
            return "Microsoft Excel OpenXML (.xlsx)"
        elif ext == ".xls":
            return "Microsoft Excel Binary 97-2003 (.xls)"
        elif ext == ".csv":
            return "Comma-Separated Values (.csv)"
        return f"Spreadsheet Document ({ext})"

    @staticmethod
    def _clean_dataframe_headers(df: pd.DataFrame) -> pd.DataFrame:
        """
        Detects if row 0 was not the actual header (e.g., title rows or lots of 'Unnamed:' columns)
        and promotes the real header row, dropping empty leading rows/columns.
        """
        if df.empty:
            return df

        # Count how many columns start with 'Unnamed:'
        unnamed_count = sum(1 for c in df.columns if str(c).startswith("Unnamed:"))
        if unnamed_count > len(df.columns) / 2:
            # Check the first 8 rows to find the row with the most non-null valid string cells
            best_row_idx = None
            max_valid_headers = 0
            for r_idx in range(min(8, len(df))):
                row_vals = df.iloc[r_idx]
                valid_count = sum(1 for v in row_vals if pd.notnull(v) and str(v).strip() and not str(v).startswith("Unnamed:"))
                if valid_count > max_valid_headers and valid_count >= 2:
                    max_valid_headers = valid_count
                    best_row_idx = r_idx

            if best_row_idx is not None:
                new_headers = []
                for idx, v in enumerate(df.iloc[best_row_idx]):
                    name = str(v).strip() if pd.notnull(v) and str(v).strip() else f"Col_{idx+1}"
                    new_headers.append(name)
                df = df.iloc[best_row_idx + 1:].copy().reset_index(drop=True)
                df.columns = new_headers
                # Drop columns that are completely all-NaN
                df = df.dropna(axis=1, how="all")
                df = df.dropna(how="all").reset_index(drop=True)

        # Clean column names (strip whitespace and remove pure Unnamed if possible)
        df.columns = [str(c).strip() for c in df.columns]
        return df

    @staticmethod
    def infer_domain(columns: List[str]) -> str:
        """Infers the business/data domain from column names"""
        col_str = " ".join([c.lower() for c in columns if not str(c).startswith("Unnamed:")])
        if any(k in col_str for k in ["project", "task", "assigned", "progress", "days required", "deadline"]):
            return "Project Management & Operations"
        if any(k in col_str for k in ["revenue", "profit", "margin", "cost", "tax", "budget", "balance"]):
            return "Financial & Accounting"
        if any(k in col_str for k in ["sale", "order", "product", "customer", "quantity", "discount"]):
            return "Sales & E-Commerce"
        if any(k in col_str for k in ["inventory", "stock", "warehouse", "sku", "supplier", "shipping"]):
            return "Inventory & Supply Chain"
        if any(k in col_str for k in ["employee", "salary", "department", "hire_date", "payroll", "designation"]):
            return "HR & Workforce"
        if any(k in col_str for k in ["patient", "diagnosis", "dosage", "treatment", "doctor", "hospital"]):
            return "Healthcare & Clinical"
        return "Tabular Analytics Dataset"

    @staticmethod
    def generate_dynamic_suggestions(sheets_data: Dict[str, Any]) -> List[str]:
        """Generates dynamic queries tailored directly to actual column names, ignoring dummy Unnamed columns"""
        suggestions = []
        if not sheets_data:
            return ["What is the total count of rows?", "Summarize this spreadsheet."]

        first_sheet = next(iter(sheets_data.values()))
        cols = first_sheet.get("columns", [])
        
        # Filter out any column named Unnamed:* or Col_*
        clean_cols = [c for c in cols if not str(c.get("name", "")).startswith("Unnamed:") and not str(c.get("name", "")).startswith("Col_")]
        if not clean_cols:
            clean_cols = cols

        numeric_cols = [c["name"] for c in clean_cols if c.get("data_type") == "numeric"]
        text_cols = [c["name"] for c in clean_cols if c.get("data_type") == "text"]
        datetime_cols = [c["name"] for c in clean_cols if c.get("data_type") == "datetime"]

        # 1. Total or Average metric
        if numeric_cols:
            suggestions.append(f"What is the average {numeric_cols[0]}?")
            suggestions.append(f"What is the total {numeric_cols[0]}?")

        # 2. Group by / Categorical comparison
        if numeric_cols and text_cols:
            suggestions.append(f"Calculate the average {numeric_cols[0]} for each {text_cols[0]}.")
            suggestions.append(f"Create a bar chart comparing {numeric_cols[0]} by {text_cols[0]}.")
            suggestions.append(f"Which {text_cols[0]} has the highest {numeric_cols[0]}?")

        # 3. Time-series / Line chart
        if datetime_cols and numeric_cols:
            suggestions.append(f"Show trend of {numeric_cols[0]} over time as a line chart.")

        # 4. Formula suggestion
        if numeric_cols:
            suggestions.append(f"Give me an Excel formula to calculate the average of {numeric_cols[0]}.")

        # Fallback if too few
        if len(suggestions) < 3:
            suggestions.append("Summarize key column distributions and null values.")

        return suggestions[:6]

    @staticmethod
    def inspect_file(filepath: str) -> Dict[str, Any]:
        """
        Inspects an Excel or CSV file and extracts sheet names, columns, headers,
        inferred data types, basic summary statistics, preview rows, and dynamic questions.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        file_type = ExcelService.detect_file_type(filepath)

        # Check if CSV
        if filepath.lower().endswith(".csv"):
            df = pd.read_csv(filepath)
            df = ExcelService._clean_dataframe_headers(df)
            sheet_names = ["Sheet1"]
            sheets_data = {"Sheet1": ExcelService._extract_sheet_metadata(df, "Sheet1")}
        else:
            excel_file = pd.ExcelFile(filepath, engine="openpyxl")
            sheet_names = excel_file.sheet_names
            sheets_data = {}
            for sheet in sheet_names:
                df = pd.read_excel(filepath, sheet_name=sheet, engine="openpyxl")
                df = ExcelService._clean_dataframe_headers(df)
                sheets_data[sheet] = ExcelService._extract_sheet_metadata(df, sheet)

        total_rows = sum(s["row_count"] for s in sheets_data.values())
        total_columns = sum(s["column_count"] for s in sheets_data.values())
        
        all_cols = []
        for s in sheets_data.values():
            all_cols.extend([c["name"] for c in s.get("columns", [])])

        inferred_domain = ExcelService.infer_domain(all_cols)
        dynamic_suggestions = ExcelService.generate_dynamic_suggestions(sheets_data)

        return {
            "file_type": file_type,
            "sheet_names": sheet_names,
            "sheets": sheets_data,
            "total_rows": total_rows,
            "total_columns": total_columns,
            "inferred_domain": inferred_domain,
            "dynamic_suggestions": dynamic_suggestions
        }

    @staticmethod
    def _extract_sheet_metadata(df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        columns_meta = []
        for idx, col in enumerate(df.columns, start=1):
            col_letter = get_column_letter(idx)
            series = df[col]
            dtype_str = str(series.dtype)
            
            # Categorize data type using pandas api types
            if pd.api.types.is_numeric_dtype(series):
                category = "numeric"
                min_v = float(series.min()) if not series.empty and pd.notnull(series.min()) else None
                max_v = float(series.max()) if not series.empty and pd.notnull(series.max()) else None
                mean_v = float(round(series.mean(), 2)) if not series.empty and pd.notnull(series.mean()) else None
            elif pd.api.types.is_datetime64_any_dtype(series):
                category = "datetime"
                min_v = str(series.min()) if not series.empty and pd.notnull(series.min()) else None
                max_v = str(series.max()) if not series.empty and pd.notnull(series.max()) else None
                mean_v = None
            elif pd.api.types.is_bool_dtype(series):
                category = "boolean"
                min_v, max_v, mean_v = None, None, None
            else:
                category = "text"
                min_v, max_v, mean_v = None, None, None

            # Get clean sample values (JSON-serializable)
            clean_samples = []
            sample_candidates = series.dropna().unique()[:5]
            for val in sample_candidates:
                if isinstance(val, (np.integer, int)):
                    clean_samples.append(int(val))
                elif isinstance(val, (np.floating, float)):
                    clean_samples.append(float(round(val, 2)))
                elif isinstance(val, (pd.Timestamp, np.datetime64)):
                    clean_samples.append(str(val)[:10])
                else:
                    clean_samples.append(str(val))

            columns_meta.append({
                "name": str(col),
                "column_letter": col_letter,
                "data_type": category,
                "raw_dtype": dtype_str,
                "non_null_count": int(series.count()),
                "null_count": int(series.isnull().sum()),
                "sample_values": clean_samples,
                "min_val": min_v,
                "max_val": max_v,
                "mean_val": mean_v
            })

        # Preview rows (convert timestamps and NaN to JSON safe representations)
        preview_df = df.head(10).copy()
        preview_rows = []
        for _, row in preview_df.iterrows():
            row_dict = {}
            for col in df.columns:
                val = row[col]
                if pd.isnull(val):
                    row_dict[str(col)] = "-"
                elif isinstance(val, (np.floating, float)):
                    row_dict[str(col)] = round(float(val), 2)
                elif isinstance(val, (np.integer, int)):
                    row_dict[str(col)] = int(val)
                elif isinstance(val, (pd.Timestamp, np.datetime64)):
                    row_dict[str(col)] = str(val)[:10]
                else:
                    row_dict[str(col)] = str(val)
            preview_rows.append(row_dict)

        return {
            "sheet_name": sheet_name,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": columns_meta,
            "preview_rows": preview_rows
        }

    @staticmethod
    def get_dataframe(filepath: str, sheet_name: Optional[str] = None) -> Tuple[pd.DataFrame, str]:
        """Loads DataFrame and returns (dataframe, sheet_name_used)"""
        if filepath.lower().endswith(".csv"):
            df = pd.read_csv(filepath)
            return ExcelService._clean_dataframe_headers(df), "Sheet1"
            
        excel_file = pd.ExcelFile(filepath, engine="openpyxl")
        target_sheet = sheet_name if sheet_name and sheet_name in excel_file.sheet_names else excel_file.sheet_names[0]
        df = pd.read_excel(filepath, sheet_name=target_sheet, engine="openpyxl")
        return ExcelService._clean_dataframe_headers(df), target_sheet

    @staticmethod
    def get_column_letter_for_name(filepath: str, sheet_name: str, col_name: str) -> Optional[str]:
        """Finds the column letter (A, B, C...) for a column header name"""
        df, _ = ExcelService.get_dataframe(filepath, sheet_name)
        for idx, col in enumerate(df.columns, start=1):
            if str(col).strip().lower() == col_name.strip().lower():
                return get_column_letter(idx)
        return None

    @staticmethod
    def create_modified_workbook(
        filepath: str,
        output_path: str,
        sheet_name: Optional[str] = None,
        new_column_header: Optional[str] = None,
        formula_template: Optional[str] = None,
        summary_table: Optional[pd.DataFrame] = None,
        chart_image_path: Optional[str] = None
    ) -> str:
        """
        Creates a modified copy of the workbook:
        - Injects an Excel formula column for all rows (e.g. `=J2-K2`)
        - Adds an 'AI_Summary' worksheet with summary statistics / tables
        - Embeds the generated chart image directly into Excel using openpyxl
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        wb = openpyxl.load_workbook(filepath)
        
        target_sheet_name = sheet_name if sheet_name and sheet_name in wb.sheetnames else wb.sheetnames[0]
        ws = wb[target_sheet_name]

        # 1. Inject formula column if specified
        if new_column_header and formula_template:
            new_col_idx = ws.max_column + 1
            new_col_letter = get_column_letter(new_col_idx)
            
            # Header
            header_cell = ws.cell(row=1, column=new_col_idx, value=new_column_header)
            header_cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            header_cell.fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
            header_cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # Fill formulas row by row
            # formula_template can have placeholder {row}, e.g. "=J{row}-K{row}"
            for row_num in range(2, ws.max_row + 1):
                cell_formula = formula_template.replace("{row}", str(row_num))
                cell = ws.cell(row=row_num, column=new_col_idx, value=cell_formula)
                cell.number_format = '#,##0.00'

            ws.column_dimensions[new_col_letter].width = max(len(new_column_header) + 4, 15)

        # 2. Add 'AI_Analysis_Summary' sheet if summary table or chart exists
        if summary_table is not None or chart_image_path:
            summary_sheet_title = "AI_Analysis_Summary"
            if summary_sheet_title in wb.sheetnames:
                del wb[summary_sheet_title]
            sum_ws = wb.create_sheet(title=summary_sheet_title)

            # Style title
            title_cell = sum_ws.cell(row=1, column=1, value="AI Excel Assistant - Analysis & Summary")
            title_cell.font = Font(name="Calibri", size=14, bold=True, color="1F4E79")

            current_row = 3
            if summary_table is not None and not summary_table.empty:
                # Write summary table headers
                for col_idx, col_name in enumerate(summary_table.columns, start=1):
                    c = sum_ws.cell(row=current_row, column=col_idx, value=str(col_name))
                    c.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
                    c.fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
                    c.alignment = Alignment(horizontal="center")
                
                # Write summary data
                for row_data in summary_table.itertuples(index=False):
                    current_row += 1
                    for col_idx, val in enumerate(row_data, start=1):
                        c = sum_ws.cell(row=current_row, column=col_idx, value=val)
                        if isinstance(val, (int, float)):
                            c.number_format = '#,##0.00'

                current_row += 3

            # 3. Embed Chart into worksheet
            if chart_image_path and os.path.exists(chart_image_path):
                img = openpyxl.drawing.image.Image(chart_image_path)
                img.width = 600
                img.height = 360
                chart_anchor = f"A{current_row}"
                sum_ws.add_image(img, chart_anchor)

            for col in sum_ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                sum_ws.column_dimensions[col_letter].width = max(max_len + 3, 15)

        wb.save(output_path)
        return output_path

excel_service = ExcelService()
