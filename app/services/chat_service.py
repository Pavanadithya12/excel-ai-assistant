import os
import json
import logging
from typing import Dict, Any, Optional
import pandas as pd
from sqlalchemy.orm import Session

from app.models.excel_file import ExcelFile
from app.models.chat import ChatSession, ChatMessage
from app.models.history import AnalysisHistory
from app.models.user import User

from app.services.excel_service import excel_service
from app.services.llm_service import llm_service
from app.services.formula_service import formula_service
from app.services.analysis_service import analysis_service
from app.services.chart_service import chart_service
from app.services.web_research_service import web_research_service

logger = logging.getLogger("chat_service")

class ChatOrchestratorService:
    @staticmethod
    def process_user_query(
        db: Session,
        user: Optional[User],
        question: str,
        file_id: Optional[int] = None,
        session_id: Optional[int] = None,
        sheet_name: Optional[str] = None,
        enable_web_research: bool = False,
        modify_excel: bool = False
    ) -> Dict[str, Any]:
        """
        Processes a natural language query end-to-end:
        1. Identifies chat session and loaded Excel file.
        2. Web research (if requested or for external benchmark queries).
        3. LLM spreadsheet interpretation.
        4. Formula generation, Pandas data analysis, and Matplotlib chart generation.
        5. Optionally creates a modified Excel file.
        6. Persists conversation and analysis history to SQL.
        """
        # 1. Resolve or gracefully create ChatSession (never crash if session_id is missing/deleted)
        chat_session = None
        if session_id:
            chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if chat_session and user and chat_session.user_id and chat_session.user_id != user.id:
                chat_session = None
            if chat_session and not file_id and chat_session.file_id:
                file_id = chat_session.file_id

        if not chat_session:
            title = question[:35] + ("..." if len(question) > 35 else "")
            chat_session = ChatSession(
                user_id=user.id if user else None,
                file_id=file_id,
                title=title
            )
            db.add(chat_session)
            db.commit()
            db.refresh(chat_session)

        # 2. Record User Message in Chat
        user_msg = ChatMessage(
            session_id=chat_session.id,
            role="user",
            content=question,
            query_type="user_query"
        )
        db.add(user_msg)
        db.commit()

        # 3. Load Excel File & Metadata if available
        excel_record = None
        df = None
        metadata = {}
        target_sheet = sheet_name

        if file_id:
            excel_record = db.query(ExcelFile).filter(ExcelFile.id == file_id).first()
            if excel_record and os.path.exists(excel_record.filepath):
                metadata = json.loads(excel_record.metadata_json) if excel_record.metadata_json else {}
                df, target_sheet = excel_service.get_dataframe(excel_record.filepath, sheet_name)

        # 4. Direct High-Accuracy DataFrame Query Check
        # Answers preview, unique values, unique counts, row counts, and data types with 100% precision
        direct_result = None
        if df is not None and not df.empty:
            direct_result = ChatOrchestratorService._handle_direct_dataframe_query(
                df=df, question=question, target_sheet=target_sheet, metadata=metadata
            )

        if direct_result:
            final_content = direct_result["content"]
            query_type = direct_result.get("query_type", "analysis")
            analysis_result = direct_result.get("analysis_result")
            formula_str = None
            formula_exp = None
            chart_url = None
            chart_type = None
            modified_file_url = None
        else:
            # 5. Optional Web Research
            web_res_summary = None
            if enable_web_research or (not excel_record and any(k in question.lower() for k in ["what is", "how to", "best practice", "formula for", "benchmark"])):
                web_info = web_research_service.search_and_synthesize(question)
                web_res_summary = web_info.get("synthesized_response")

            # 6. LLM / Heuristic Interpretation
            plan = llm_service.interpret_question(question, metadata, target_sheet)
            query_type = plan.get("query_type", "general")
            explanation = plan.get("explanation", "")

            formula_str = None
            formula_exp = None
            analysis_result = None
            chart_url = None
            chart_type = None
            chart_path = None
            modified_file_url = None
            summary_df_for_excel = None

            # 7. Execute based on plan
            if df is not None and not df.empty:
                # A. FORMULA GENERATION
                if plan.get("formula"):
                    f_info = plan["formula"]
                    formula_str = f_info.get("formula_string")
                    formula_exp = f_info.get("explanation")
                    v_res = formula_service.validate_formula(formula_str)
                    if not v_res["is_valid"]:
                        explanation += f" (Note: {v_res['message']})"

                # B. PANDAS DATA ANALYSIS
                if plan.get("analysis"):
                    a_info = plan["analysis"]
                    op = a_info.get("operation")
                    try:
                        if op == "sum" or op == "average":
                            col = a_info.get("column") or a_info.get("value_column")
                            # Guard: skip if column is None or not in dataframe
                            if not col or col not in df.columns:
                                numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
                                col = numeric_cols[0] if numeric_cols else None
                            if col and col in df.columns:
                                analysis_result = analysis_service.calculate_total_or_metric(df, col, metric=op)
                        elif op == "groupby":
                            grp = a_info.get("group_column")
                            val = a_info.get("value_column")
                            agg = a_info.get("agg_func", "sum")
                            analysis_result = analysis_service.group_by_and_aggregate(df, grp, val, agg_func=agg)
                            summary_df_for_excel = pd.DataFrame(analysis_result.get("rows", []))
                        elif op == "top_n":
                            grp = a_info.get("group_column")
                            val = a_info.get("value_column")
                            n = a_info.get("n", 10)
                            analysis_result = analysis_service.get_top_n(df, grp, val, n=n)
                            summary_df_for_excel = pd.DataFrame(analysis_result.get("rows", []))
                        elif op == "extreme":
                            grp = a_info.get("group_column")
                            val = a_info.get("value_column")
                            ext = a_info.get("extreme", "highest")
                            analysis_result = analysis_service.get_extreme_entity(df, grp, val, extreme=ext)
                        elif op == "difference":
                            act = a_info.get("actual_column")
                            tgt = a_info.get("target_column")
                            analysis_result = analysis_service.calculate_column_difference(df, act, tgt)
                    except Exception as e:
                        logger.error(f"Analysis error: {e}")
                        analysis_result = {"error": str(e)}

                # C. CHART GENERATION
                if plan.get("chart"):
                    c_info = plan["chart"]
                    try:
                        c_res = chart_service.generate_chart(
                            df=df,
                            chart_type=c_info.get("chart_type", "bar"),
                            x_col=c_info.get("x_column"),
                            y_col=c_info.get("y_column"),
                            title=c_info.get("title")
                        )
                        chart_url = c_res["url"]
                        chart_type = c_res["chart_type"]
                        chart_path = c_res["filepath"]
                    except Exception as e:
                        logger.error(f"Chart error: {e}")

                # D. OPTIONALLY MODIFY EXCEL WORKBOOK
                if modify_excel or (plan.get("formula") and plan["formula"].get("new_column_header")):
                    try:
                        mod_filename = f"modified_{os.path.basename(excel_record.filepath)}"
                        mod_path = os.path.join(os.path.dirname(excel_record.filepath), mod_filename)
                        f_head = plan["formula"].get("new_column_header") if plan.get("formula") else None
                        f_tpl = plan["formula"].get("formula_string") if plan.get("formula") else None
                        if f_tpl:
                            f_tpl = f_tpl.replace("2", "{row}")
                        
                        excel_service.create_modified_workbook(
                            filepath=excel_record.filepath,
                            output_path=mod_path,
                            sheet_name=target_sheet,
                            new_column_header=f_head,
                            formula_template=f_tpl,
                            summary_table=summary_df_for_excel,
                            chart_image_path=chart_path
                        )
                        excel_record.modified_filepath = mod_path
                        db.commit()
                        modified_file_url = f"/api/excel/{excel_record.id}/download-modified"
                    except Exception as e:
                        logger.error(f"Modify Excel error: {e}")

            # Combine explanation with web research if applicable
            final_content = explanation
            if web_res_summary:
                final_content += f"\n\n🔍 **Web Research Finding**:\n{web_res_summary}"

        # 7. Persist Assistant Response in DB
        assistant_msg = ChatMessage(
            session_id=chat_session.id,
            role="assistant",
            content=final_content,
            query_type=query_type,
            formula=formula_str,
            formula_explanation=formula_exp,
            analysis_result=json.dumps(analysis_result) if analysis_result else None,
            chart_url=chart_url,
            chart_type=chart_type,
            modified_file_url=modified_file_url
        )
        db.add(assistant_msg)

        # 8. Store in AnalysisHistory in SQL
        history_item = AnalysisHistory(
            user_id=user.id if user else None,
            file_id=file_id,
            session_id=chat_session.id,
            question=question,
            operation_type=query_type,
            sheet_name=target_sheet,
            formula_generated=formula_str,
            summary_result=json.dumps(analysis_result) if analysis_result else final_content,
            chart_path=chart_url
        )
        db.add(history_item)
        db.commit()
        db.refresh(assistant_msg)

        return {
            "session_id": chat_session.id,
            "message_id": assistant_msg.id,
            "role": "assistant",
            "content": final_content,
            "query_type": query_type,
            "formula": formula_str,
            "formula_explanation": formula_exp,
            "analysis_result": analysis_result,
            "chart_url": chart_url,
            "chart_type": chart_type,
            "modified_file_url": modified_file_url,
            "created_at": assistant_msg.created_at
        }

    @staticmethod
    def _handle_direct_dataframe_query(
        df: pd.DataFrame,
        question: str,
        target_sheet: Optional[str] = "Sheet1",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Directly answers core data exploration questions with 100% precision:
        - Previews of first N rows
        - Unique values in a specific column
        - Count of unique entries in a column
        - Row & column counts / dataset size
        - Column data types and non-null summary
        - Distribution and quality audit
        """
        import re
        q_lower = question.lower().strip()
        col_map = {str(c).strip().lower(): str(c) for c in df.columns}

        # Helper to find column mentioned in question (ordered by longest first to avoid partial matches)
        sorted_cols = sorted(col_map.items(), key=lambda x: len(x[0]), reverse=True)
        def find_mentioned_col() -> Optional[str]:
            for col_l, col_orig in sorted_cols:
                if col_l in q_lower:
                    return col_orig
            return None

        # 1. PREVIEW / FIRST N ROWS
        if any(k in q_lower for k in ["preview", "first 10 rows", "first 5 rows", "sample data", "show rows", "show me a preview"]):
            m = re.search(r"(?:first|top)\s*(\d+)", q_lower)
            n = int(m.group(1)) if m else 10
            n = min(max(n, 1), 50)
            sample_df = df.head(n)

            table_records = []
            for idx, r in sample_df.iterrows():
                row_dict = {"#": int(idx) + 1}
                for c in sample_df.columns:
                    val = r[c]
                    row_dict[str(c)] = str(val) if pd.notnull(val) else "-"
                table_records.append(row_dict)

            content = f"📋 **First {len(sample_df)} Rows Preview — '{target_sheet}'**\n\nDisplaying {len(sample_df)} of {len(df):,} total records:"
            return {
                "content": content,
                "query_type": "analysis",
                "analysis_result": {
                    "is_table": True,
                    "columns": ["#"] + list(sample_df.columns),
                    "rows": table_records
                }
            }

        # 2. HOW MANY UNIQUE ENTRIES IN [COL]
        if ("unique" in q_lower or "distinct" in q_lower) and any(k in q_lower for k in ["how many", "count", "number of", "entries", "records"]):
            col = find_mentioned_col()
            if col:
                n_uniq = int(df[col].dropna().nunique())
                total = len(df)
                content = f"🔍 The '**{col}**' column contains **{n_uniq} unique entries** (across {total:,} total records)."
                return {
                    "content": content,
                    "query_type": "analysis",
                    "analysis_result": {
                        "metric": "unique_count",
                        "column": col,
                        "value": n_uniq,
                        "total_rows": total
                    }
                }

        # 3. SHOW UNIQUE VALUES IN [COL]
        if ("unique" in q_lower or "distinct" in q_lower or "list" in q_lower) and any(k in q_lower for k in ["values", "show", "what are", "categories"]):
            col = find_mentioned_col()
            if col:
                uniques = [str(x) for x in df[col].dropna().unique() if str(x).strip()]
                preview_list = uniques[:30]
                lines = [f"• {u}" for u in preview_list]
                extra = f"\n\n*(...and {len(uniques) - 30} more distinct values)*" if len(uniques) > 30 else ""
                content = f"🏷️ **Unique Values in '{col}'** ({len(uniques)} distinct entries):\n\n" + "\n".join(lines) + extra
                return {
                    "content": content,
                    "query_type": "analysis",
                    "analysis_result": {
                        "column": col,
                        "unique_count": len(uniques),
                        "values": preview_list
                    }
                }

        # 4. HOW MANY ROWS AND COLUMNS / HOW MANY DATA
        if any(k in q_lower for k in ["how many rows", "how many columns", "how many data", "how much data", "total rows and columns", "dataset dimension"]):
            rows = len(df)
            cols = len(df.columns)
            total_cells = rows * cols
            col_list = ", ".join(f"`{c}`" for c in df.columns)
            content = (
                f"📊 **Document Dimensions — '{target_sheet}'**\n\n"
                f"• **Total Records / Rows:** {rows:,}\n"
                f"• **Total Columns:** {cols}\n"
                f"• **Total Data Cells:** {total_cells:,}\n\n"
                f"**Columns:** {col_list}"
            )
            return {
                "content": content,
                "query_type": "general",
                "analysis_result": None
            }

        # 5. WHAT DATA TYPES ARE IN EACH COLUMN / SCHEMA
        if any(k in q_lower for k in ["data type", "data types", "column types", "what types", "schema"]):
            type_rows = []
            for col in df.columns:
                s = df[col]
                num_s = pd.to_numeric(s, errors='coerce')
                num_ratio = num_s.notnull().sum() / max(1, s.notnull().sum())
                if num_ratio >= 0.7:
                    cat = "Numeric"
                else:
                    dt_s = pd.to_datetime(s, errors='coerce')
                    dt_ratio = dt_s.notnull().sum() / max(1, s.notnull().sum())
                    if dt_ratio >= 0.7:
                        cat = "Datetime"
                    else:
                        cat = "Text"
                non_null = int(s.notnull().sum())
                type_rows.append({"Column Name": col, "Data Type": cat, "Non-Null Count": non_null, "Null Count": int(s.isnull().sum())})

            lines = [f"• **{r['Column Name']}**: {r['Data Type']} ({r['Non-Null Count']} values)" for r in type_rows]
            content = f"🗂️ **Column Data Types — '{target_sheet}'** ({len(df.columns)} columns):\n\n" + "\n".join(lines)
            return {
                "content": content,
                "query_type": "analysis",
                "analysis_result": {
                    "is_table": True,
                    "columns": ["Column Name", "Data Type", "Non-Null Count", "Null Count"],
                    "rows": type_rows
                }
            }

        # 6. SUMMARIZE KEY COLUMN DISTRIBUTIONS AND NULL VALUES
        if any(k in q_lower for k in ["distribution", "null value", "null values", "missing values", "summarize key"]):
            rows = len(df)
            cols = len(df.columns)

            stats_lines = []
            for c in df.columns:
                s = df[c]
                num_s = pd.to_numeric(s, errors='coerce').dropna()
                if not num_s.empty and len(num_s) / max(1, s.notnull().sum()) >= 0.6:
                    stats_lines.append(f"  • **{c}**: min={num_s.min():.2f}, max={num_s.max():.2f}, avg={num_s.mean():.2f}")
            num_section = "\n".join(stats_lines) if stats_lines else "  • No predominantly numeric columns detected."

            null_lines = []
            for c in df.columns:
                n_null = int(df[c].isnull().sum())
                if n_null > 0:
                    pct = (n_null / rows) * 100
                    null_lines.append(f"  • **{c}**: {n_null} missing ({pct:.1f}%)")
            null_section = "\n".join(null_lines) if null_lines else "  • Zero null/missing values (100% complete dataset)."

            content = (
                f"📊 **Comprehensive Distribution & Quality Audit — '{target_sheet}'**\n\n"
                f"• **Total Records:** {rows:,} rows × {cols} columns\n\n"
                f"**🔢 Numeric Distributions:**\n{num_section}\n\n"
                f"**⚠️ Null & Missing Value Report:**\n{null_section}"
            )
            return {
                "content": content,
                "query_type": "general",
                "analysis_result": None
            }

        return None

chat_service = ChatOrchestratorService()
