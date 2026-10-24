import os
import re
import json
import logging
from typing import Dict, Any, Optional, List
from app.config import settings

logger = logging.getLogger("llm_service")

class LLMService:
    def __init__(self):
        self.gemini_client = None
        self.openai_client = None
        self._init_clients()

    def _init_clients(self):
        # Gemini setup
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Initialized Google Gemini client.")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}")

        # OpenAI setup
        if settings.OPENAI_API_KEY:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("Initialized OpenAI client.")
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")

    def interpret_question(
        self,
        question: str,
        spreadsheet_metadata: Dict[str, Any],
        active_sheet: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Interprets natural language question against spreadsheet metadata.
        Uses Gemini or OpenAI if configured, or the smart fallback engine.
        """
        # Select active sheet
        sheet_names = spreadsheet_metadata.get("sheet_names", [])
        sheet_name = active_sheet if active_sheet and active_sheet in sheet_names else (sheet_names[0] if sheet_names else "Sheet1")
        sheet_info = spreadsheet_metadata.get("sheets", {}).get(sheet_name, {})
        columns = sheet_info.get("columns", [])

        # Try LLM if configured
        if self.gemini_client:
            try:
                res = self._call_gemini(question, sheet_name, columns)
                if res and self._validate_columns_in_plan(res, columns):
                    return res
            except Exception as e:
                logger.warning(f"Gemini interpretation failed, falling back: {e}")

        if self.openai_client:
            try:
                res = self._call_openai(question, sheet_name, columns)
                if res and self._validate_columns_in_plan(res, columns):
                    return res
            except Exception as e:
                logger.warning(f"OpenAI interpretation failed, falling back: {e}")

        # Smart Fallback Engine
        return self._smart_rule_engine(question, sheet_name, columns, sheet_info.get("row_count", 100))

    def _validate_columns_in_plan(self, plan: Dict[str, Any], columns: List[Dict[str, Any]]) -> bool:
        """Never invent column names: verify plan references only real columns"""
        col_names = {c["name"].lower() for c in columns}
        
        # Check chart columns
        chart_plan = plan.get("chart")
        if chart_plan:
            x_col = chart_plan.get("x_column")
            y_col = chart_plan.get("y_column")
            if x_col and x_col.lower() not in col_names:
                return False
            if y_col and y_col.lower() not in col_names:
                return False

        # Check analysis columns
        analysis_plan = plan.get("analysis")
        if analysis_plan:
            val_col = analysis_plan.get("value_column")
            grp_col = analysis_plan.get("group_column")
            if val_col and val_col.lower() not in col_names:
                return False
            if grp_col and grp_col.lower() not in col_names:
                return False

        return True

    def _call_gemini(self, question: str, sheet_name: str, columns: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        col_summary = ", ".join([f"{c['name']} (Col {c['column_letter']}, Type: {c['data_type']})" for c in columns])
        prompt = f"""
You are an expert AI Excel Assistant.
Spreadsheet Sheet: "{sheet_name}"
Available Columns: {col_summary}

User Question: "{question}"

Rules:
1. NEVER invent column names or data not in the available columns.
2. Determine query_type: "formula", "analysis", "chart", "web_research", or "general".
3. Return STRICT VALID JSON only matching this schema:
{{
  "query_type": "formula|analysis|chart|web_research|general",
  "explanation": "Clear explanation of what is calculated or shown",
  "formula": {{
    "operation": "sum|average|difference|profit_margin|countif|sumif|vlookup|xlookup",
    "formula_string": "=EXCEL_FORMULA",
    "target_column": "ColumnName",
    "secondary_column": "ColumnName or null",
    "new_column_header": "Header name for new column"
  }} or null,
  "analysis": {{
    "operation": "sum|average|min|max|groupby|top_n|extreme|difference",
    "group_column": "ColumnName or null",
    "value_column": "ColumnName or null",
    "n": 10,
    "extreme": "highest|lowest"
  }} or null,
  "chart": {{
    "chart_type": "bar|line|pie|scatter",
    "x_column": "ColumnName",
    "y_column": "ColumnName or null",
    "title": "Chart Title"
  }} or null
}}
"""
        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text.strip()
        # Clean markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

    def _call_openai(self, question: str, sheet_name: str, columns: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        col_summary = ", ".join([f"{c['name']} (Col {c['column_letter']}, Type: {c['data_type']})" for c in columns])
        prompt = f"""
You are an expert AI Excel Assistant.
Spreadsheet Sheet: "{sheet_name}"
Available Columns: {col_summary}

User Question: "{question}"

Rules:
1. NEVER invent column names or data not in the available columns.
2. Determine query_type: "formula", "analysis", "chart", "web_research", or "general".
3. Return STRICT JSON with query_type, explanation, formula, analysis, and chart objects.
"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def _smart_rule_engine(
        self,
        question: str,
        sheet_name: str,
        columns: List[Dict[str, Any]],
        row_count: int
    ) -> Dict[str, Any]:
        """
        Smart fallback engine: Parses natural language intent, finds matching
        columns with high precision, and formulates the correct operation.
        """
        q_lower = question.lower()
        col_map = {c["name"].lower(): c for c in columns}

        # Guard: if no columns at all, return a safe general response
        if not columns:
            return {
                "query_type": "general",
                "explanation": "No column metadata is available for this spreadsheet. Please re-upload the file.",
                "formula": None,
                "analysis": None,
                "chart": None
            }

        # Helper to find closest column name
        def match_column(keywords: List[str], preferred_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
            # Exact match
            for kw in keywords:
                if kw in col_map:
                    if not preferred_type or col_map[kw]["data_type"] == preferred_type:
                        return col_map[kw]
            # Substring match
            for kw in keywords:
                for c_name, c_info in col_map.items():
                    if kw in c_name:
                        if not preferred_type or c_info["data_type"] == preferred_type:
                            return c_info
            # Fallback to first column matching preferred_type
            if preferred_type:
                for c_info in columns:
                    if c_info["data_type"] == preferred_type:
                        return c_info
            return None

        # Detect columns
        sales_col = match_column(["actualsales", "sales", "revenue", "amount", "total"], "numeric")
        target_col = match_column(["targetsales", "target", "budget", "goal"], "numeric")
        profit_col = match_column(["profit", "margin", "net"], "numeric")
        cost_col = match_column(["totalcost", "cost", "unitcost"], "numeric")
        region_col = match_column(["region", "territory", "area", "zone", "state", "country"], "text")
        product_col = match_column(["product", "item", "sku", "category"], "text")
        customer_col = match_column(["customer", "client", "account", "company"], "text")
        date_col = match_column(["orderdate", "date", "month", "year", "time"], "datetime") or match_column(["orderdate", "date"])

        # Default numeric and text fallbacks
        first_numeric = next((c for c in columns if c["data_type"] == "numeric"), None)
        first_text = next((c for c in columns if c["data_type"] == "text"), None)

        # 1. CHART INTENT
        is_chart = any(k in q_lower for k in ["chart", "plot", "graph", "visualize", "show", "display"]) and any(k in q_lower for k in ["bar", "line", "pie", "scatter", "histogram", "trend"])
        if is_chart or "chart" in q_lower or "graph" in q_lower or "plot" in q_lower:
            chart_type = "bar"
            if "line" in q_lower or "trend" in q_lower or "monthly" in q_lower:
                chart_type = "line"
            elif "pie" in q_lower or "share" in q_lower:
                chart_type = "pie"
            elif "scatter" in q_lower or "correlation" in q_lower:
                chart_type = "scatter"

            # Determine x and y
            if chart_type == "line" and date_col:
                x_c = date_col["name"]
                y_c = (sales_col or first_numeric)["name"] if (sales_col or first_numeric) else None
                title = f"Monthly {y_c or 'Metric'} Trend"
            elif region_col and ("region" in q_lower or not customer_col):
                x_c = region_col["name"]
                y_c = (sales_col or first_numeric)["name"] if (sales_col or first_numeric) else None
                title = f"{y_c or 'Metric'} by {x_c}"
            elif product_col and "product" in q_lower:
                x_c = product_col["name"]
                y_c = (sales_col or first_numeric)["name"] if (sales_col or first_numeric) else None
                title = f"{y_c or 'Metric'} by {x_c}"
            elif customer_col and "customer" in q_lower:
                x_c = customer_col["name"]
                y_c = (sales_col or first_numeric)["name"] if (sales_col or first_numeric) else None
                title = f"{y_c or 'Metric'} by {x_c}"
            else:
                x_c = (first_text or columns[0])["name"]
                y_c = first_numeric["name"] if first_numeric else None
                title = f"{chart_type.capitalize()} Chart: {x_c}"

            return {
                "query_type": "chart",
                "explanation": f"Generated a {chart_type} chart illustrating '{title}'.",
                "chart": {
                    "chart_type": chart_type,
                    "x_column": x_c,
                    "y_column": y_c,
                    "title": title
                },
                "analysis": {
                    "operation": "groupby",
                    "group_column": x_c,
                    "value_column": y_c or (first_numeric["name"] if first_numeric else x_c)
                }
            }

        # 2. FORMULA INTENT
        is_formula = any(k in q_lower for k in ["formula", "excel formula", "calculate formula", "add formula", "write formula"])
        if is_formula:
            # Profit margin formula
            if "profit" in q_lower and "margin" in q_lower:
                p_letter = profit_col["column_letter"] if profit_col else "M"
                s_letter = sales_col["column_letter"] if sales_col else "J"
                return {
                    "query_type": "formula",
                    "explanation": f"Excel formula to calculate profit margin: Divide Profit (Col {p_letter}) by Actual Sales (Col {s_letter}), checking for zero.",
                    "formula": {
                        "operation": "profit_margin",
                        "formula_string": f"=IF({s_letter}2>0, {p_letter}2/{s_letter}2, 0)",
                        "target_column": profit_col["name"] if profit_col else "Profit",
                        "secondary_column": sales_col["name"] if sales_col else "ActualSales",
                        "new_column_header": "ProfitMargin",
                        "explanation": f"=IF({s_letter}2>0, {p_letter}2/{s_letter}2, 0) - evaluates margin percentage row-by-row."
                    }
                }
            # Difference formula (Actual - Target)
            if "difference" in q_lower or ("actual" in q_lower and "target" in q_lower):
                a_letter = sales_col["column_letter"] if sales_col else "J"
                t_letter = target_col["column_letter"] if target_col else "K"
                return {
                    "query_type": "formula",
                    "explanation": f"Excel formula to calculate variance: Actual Sales (Col {a_letter}) minus Target Sales (Col {t_letter}).",
                    "formula": {
                        "operation": "difference",
                        "formula_string": f"={a_letter}2-{t_letter}2",
                        "target_column": sales_col["name"] if sales_col else "ActualSales",
                        "secondary_column": target_col["name"] if target_col else "TargetSales",
                        "new_column_header": "Variance_Actual_Target",
                        "explanation": f"={a_letter}2-{t_letter}2 calculates row-level difference."
                    }
                }
            # Average formula
            if "average" in q_lower or "avg" in q_lower:
                num_c = sales_col or first_numeric
                c_let = num_c["column_letter"] if num_c else "A"
                c_name = num_c["name"] if num_c else "Metric"
                return {
                    "query_type": "formula",
                    "explanation": f"Excel formula for average of {c_name}.",
                    "formula": {
                        "operation": "average",
                        "formula_string": f"=AVERAGE({c_let}2:{c_let}{row_count + 1})",
                        "target_column": c_name,
                        "explanation": f"=AVERAGE({c_let}2:{c_let}{row_count + 1}) computes the arithmetic mean."
                    }
                }
            # VLOOKUP / XLOOKUP
            if "lookup" in q_lower or "xlookup" in q_lower or "vlookup" in q_lower:
                return {
                    "query_type": "formula",
                    "explanation": "Modern XLOOKUP formula for matching key values against reference tables.",
                    "formula": {
                        "operation": "xlookup",
                        "formula_string": "=XLOOKUP(D2, RegionalTargets!$A$2:$A$5, RegionalTargets!$B$2:$B$5, \"Not Found\")",
                        "target_column": "Region",
                        "explanation": "Looks up the regional manager from RegionalTargets sheet."
                    }
                }
            # Generic SUM formula
            num_c = sales_col or first_numeric
            c_let = num_c["column_letter"] if num_c else "A"
            c_name = num_c["name"] if num_c else "Metric"
            return {
                "query_type": "formula",
                "explanation": f"Excel formula for sum of {c_name}.",
                "formula": {
                    "operation": "sum",
                    "formula_string": f"=SUM({c_let}2:{c_let}{row_count + 1})",
                    "target_column": c_name,
                    "explanation": f"=SUM({c_let}2:{c_let}{row_count + 1}) calculates the grand total."
                }
            }

        # 3. SUMMARIZE / COUNT / DISTRIBUTION / NULL INTENT (Checked before specific metrics)
        is_summary = any(k in q_lower for k in [
            "summarize", "summary", "distribution", "null", "missing",
            "overview", "describe", "info", "statistics", "data quality",
            "how many rows", "how many records", "count rows", "total rows",
            "how many columns", "column info", "data types", "schema",
            "how many data", "how much data", "how many entries"
        ]) or (("how many" in q_lower or "count" in q_lower) and ("data" in q_lower or "record" in q_lower or "row" in q_lower))
        if is_summary:
            col_names_display = ", ".join([c["name"] for c in columns[:8]]) + ("..." if len(columns) > 8 else "")
            null_info_lines = []
            for c in columns:
                null_c = c.get("null_count", 0)
                if null_c and null_c > 0:
                    null_info_lines.append(f"  • {c['name']}: {null_c} missing value(s)")
            null_summary = "\n".join(null_info_lines) if null_info_lines else "  • No null/missing values detected (complete dataset)."

            num_cols_info = []
            for c in columns:
                if c.get("data_type") == "numeric" and c.get("mean_val") is not None:
                    num_cols_info.append(
                        f"  • {c['name']}: min={c.get('min_val')}, max={c.get('max_val')}, avg={c.get('mean_val')}"
                    )
            num_summary = "\n".join(num_cols_info) if num_cols_info else "  • No numeric columns detected."

            text_cols_list = [c["name"] for c in columns if c.get("data_type") == "text"]
            text_summary = ", ".join(text_cols_list) if text_cols_list else "None"

            explanation = (
                f"📊 **Spreadsheet Overview — '{sheet_name}'**\n\n"
                f"• **Total Records / Rows:** {row_count:,}\n"
                f"• **Total Columns:** {len(columns)}\n"
                f"• **Columns:** {col_names_display}\n\n"
                f"**🔢 Numeric Statistics:**\n{num_summary}\n\n"
                f"**🔤 Text / Categories:** {text_summary}\n\n"
                f"**⚠️ Null & Missing Values:**\n{null_summary}"
            )
            return {
                "query_type": "general",
                "explanation": explanation,
                "formula": None,
                "analysis": None,
                "chart": None
            }

        # 4. ANALYSIS INTENT
        # Group by average sales for each region
        if ("average" in q_lower or "avg" in q_lower) and ("each" in q_lower or "per" in q_lower or "by" in q_lower or "region" in q_lower):
            grp_col = region_col or product_col or first_text
            val_col = sales_col or first_numeric
            if grp_col and val_col:
                return {
                    "query_type": "analysis",
                    "explanation": f"Calculated the average {val_col['name']} for each {grp_col['name']}.",
                    "analysis": {
                        "operation": "groupby",
                        "agg_func": "mean",
                        "group_column": grp_col["name"],
                        "value_column": val_col["name"]
                    }
                }

        # Highest revenue / top entity
        if any(k in q_lower for k in ["highest", "most", "maximum", "best", "top product"]):
            grp_col = product_col if "product" in q_lower else (customer_col if "customer" in q_lower else (region_col or first_text))
            val_col = sales_col or profit_col or first_numeric
            if grp_col and val_col:
                return {
                    "query_type": "analysis",
                    "explanation": f"Identified the entity with the highest {val_col['name']}.",
                    "analysis": {
                        "operation": "extreme",
                        "extreme": "highest",
                        "group_column": grp_col["name"],
                        "value_column": val_col["name"]
                    }
                }

        # Top 10 or Top N
        top_match = re.search(r"top\s*(\d+)", q_lower)
        if top_match or "top" in q_lower:
            n = int(top_match.group(1)) if top_match else 10
            grp_col = customer_col if "customer" in q_lower else (product_col if "product" in q_lower else (region_col or first_text))
            val_col = sales_col or profit_col or first_numeric
            if grp_col and val_col:
                return {
                    "query_type": "analysis",
                    "explanation": f"Found the top {n} {grp_col['name']}s by total {val_col['name']}.",
                    "analysis": {
                        "operation": "top_n",
                        "n": n,
                        "group_column": grp_col["name"],
                        "value_column": val_col["name"]
                    }
                }

        # Total sales amount / metric (use word boundaries so 'sum' doesn't match 'summarize')
        if re.search(r"\b(total|sum|grand total|overall)\b", q_lower):
            val_col = sales_col or first_numeric
            if val_col:
                return {
                    "query_type": "analysis",
                    "explanation": f"Calculated total {val_col['name']} across all records.",
                    "analysis": {
                        "operation": "sum",
                        "column": val_col["name"]
                    }
                }

        # Default fallback — guard against None numeric column
        num_c = sales_col or first_numeric
        if num_c:
            return {
                "query_type": "analysis",
                "explanation": f"Analyzed {num_c['name']} across all records in '{sheet_name}'.",
                "analysis": {
                    "operation": "sum",
                    "column": num_c["name"]
                },
                "formula": None,
                "chart": None
            }

        # Last resort: general text response about the spreadsheet
        col_names_str = ", ".join([c["name"] for c in columns[:6]])
        return {
            "query_type": "general",
            "explanation": (
                f"Your spreadsheet '{sheet_name}' contains {row_count:,} rows and {len(columns)} columns: "
                f"{col_names_str}. "
                f"Try asking questions like 'Show unique values in {columns[0]['name']}' or 'Summarize key column distributions'."
            ),
            "formula": None,
            "analysis": None,
            "chart": None
        }

llm_service = LLMService()
