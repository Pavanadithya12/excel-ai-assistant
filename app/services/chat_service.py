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
        # 1. Resolve or create ChatSession
        if session_id:
            chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not chat_session:
                raise ValueError(f"Chat session {session_id} not found.")
            if not file_id and chat_session.file_id:
                file_id = chat_session.file_id
        else:
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

        # 4. Optional Web Research
        web_res_summary = None
        if enable_web_research or (not excel_record and any(k in question.lower() for k in ["what is", "how to", "best practice", "formula for", "benchmark"])):
            web_info = web_research_service.search_and_synthesize(question)
            web_res_summary = web_info.get("synthesized_response")

        # 5. LLM Interpretation
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

        # 6. Execute based on plan
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
                        # Convert formula to row template e.g. =J2-K2 -> =J{row}-K{row}
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

chat_service = ChatOrchestratorService()
