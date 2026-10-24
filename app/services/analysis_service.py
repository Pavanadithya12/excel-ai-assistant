from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class AnalysisService:
    @staticmethod
    def _resolve_column(df: pd.DataFrame, col_name: str) -> Optional[str]:
        """Resolves a column name handling case-insensitivity and whitespace differences"""
        if not col_name or df.empty:
            return None
        if col_name in df.columns:
            return col_name
        target = col_name.strip().lower()
        for c in df.columns:
            if str(c).strip().lower() == target:
                return str(c)
        return None

    @staticmethod
    def calculate_total_or_metric(df: pd.DataFrame, col_name: str, metric: str = "sum") -> Dict[str, Any]:
        """Calculates total, average, min, max, count for a numeric column"""
        resolved = AnalysisService._resolve_column(df, col_name)
        if not resolved:
            raise ValueError(f"Column '{col_name}' not found in dataframe.")
        col_name = resolved
            
        series = pd.to_numeric(df[col_name], errors='coerce').dropna()
        if series.empty:
            return {"metric": metric, "column": col_name, "value": 0, "formatted": "0.00"}
            
        metric = metric.lower()
        if metric == "sum" or metric == "total":
            val = float(series.sum())
        elif metric in ["mean", "average", "avg"]:
            val = float(series.mean())
        elif metric == "min":
            val = float(series.min())
        elif metric == "max":
            val = float(series.max())
        elif metric == "median":
            val = float(series.median())
        elif metric == "count":
            val = int(series.count())
        else:
            val = float(series.sum())

        return {
            "metric": metric,
            "column": col_name,
            "value": round(val, 2),
            "formatted": f"{val:,.2f}" if isinstance(val, (int, float)) else str(val),
            "count": int(series.count()),
            "min": round(float(series.min()), 2),
            "max": round(float(series.max()), 2),
            "average": round(float(series.mean()), 2),
            "total": round(float(series.sum()), 2)
        }

    @staticmethod
    def group_by_and_aggregate(
        df: pd.DataFrame,
        group_col: str,
        value_col: str,
        agg_func: str = "sum"
    ) -> Dict[str, Any]:
        """Groups by a categorical column and aggregates a numeric column"""
        resolved_grp = AnalysisService._resolve_column(df, group_col)
        if not resolved_grp:
            raise ValueError(f"Group column '{group_col}' not found.")
        resolved_val = AnalysisService._resolve_column(df, value_col)
        if not resolved_val:
            raise ValueError(f"Value column '{value_col}' not found.")
        group_col = resolved_grp
        value_col = resolved_val

        work_df = df.copy()
        work_df[value_col] = pd.to_numeric(work_df[value_col], errors='coerce')
        
        grouped = work_df.groupby(group_col)[value_col].agg(agg_func).reset_index()
        grouped = grouped.sort_values(by=value_col, ascending=False)
        
        # Format table
        records = []
        for _, row in grouped.iterrows():
            v = row[value_col]
            records.append({
                str(group_col): str(row[group_col]),
                str(value_col): round(float(v), 2) if pd.notnull(v) else 0.0,
                "formatted_value": f"{v:,.2f}" if pd.notnull(v) else "0.00"
            })
            
        total_val = float(work_df[value_col].sum())
        avg_val = float(work_df[value_col].mean())
        
        return {
            "group_column": group_col,
            "value_column": value_col,
            "aggregation": agg_func,
            "rows": records,
            "summary": {
                "total": round(total_val, 2),
                "average": round(avg_val, 2),
                "count": len(records)
            }
        }

    @staticmethod
    def get_top_n(
        df: pd.DataFrame,
        group_col: str,
        value_col: str,
        n: int = 10,
        ascending: bool = False
    ) -> Dict[str, Any]:
        """Gets top (or bottom) N entities by aggregated value"""
        res = AnalysisService.group_by_and_aggregate(df, group_col, value_col, agg_func="sum")
        rows = res["rows"]
        if ascending:
            rows = sorted(rows, key=lambda x: x[value_col])
        else:
            rows = sorted(rows, key=lambda x: x[value_col], reverse=True)
            
        top_rows = rows[:n]
        return {
            "type": "top_n",
            "n": n,
            "group_column": group_col,
            "value_column": value_col,
            "rows": top_rows
        }

    @staticmethod
    def get_extreme_entity(
        df: pd.DataFrame,
        group_col: str,
        value_col: str,
        extreme: str = "highest"
    ) -> Dict[str, Any]:
        """Finds the single entity with highest or lowest aggregated value"""
        is_highest = (extreme.lower() in ["highest", "max", "top", "best"])
        res = AnalysisService.group_by_and_aggregate(df, group_col, value_col, agg_func="sum")
        if not res["rows"]:
            return {}
        target = res["rows"][0] if is_highest else res["rows"][-1]
        return {
            "extreme": "highest" if is_highest else "lowest",
            "group_column": group_col,
            "value_column": value_col,
            "entity": target[group_col],
            "value": target[value_col],
            "formatted_value": target["formatted_value"]
        }

    @staticmethod
    def calculate_column_difference(
        df: pd.DataFrame,
        actual_col: str,
        target_col: str
    ) -> Dict[str, Any]:
        """Calculates difference between two columns (Actual vs Target)"""
        resolved_act = AnalysisService._resolve_column(df, actual_col)
        resolved_tgt = AnalysisService._resolve_column(df, target_col)
        if not resolved_act or not resolved_tgt:
            raise ValueError(f"Difference columns '{actual_col}' or '{target_col}' not found.")
        actual_col = resolved_act
        target_col = resolved_tgt

        work_df = df.copy()
        work_df[actual_col] = pd.to_numeric(work_df[actual_col], errors='coerce').fillna(0)
        work_df[target_col] = pd.to_numeric(work_df[target_col], errors='coerce').fillna(0)
        
        diff_series = work_df[actual_col] - work_df[target_col]
        total_actual = float(work_df[actual_col].sum())
        total_target = float(work_df[target_col].sum())
        total_diff = float(diff_series.sum())
        
        pct_diff = (total_diff / total_target * 100) if total_target != 0 else 0.0
        
        return {
            "actual_column": actual_col,
            "target_column": target_col,
            "total_actual": round(total_actual, 2),
            "total_target": round(total_target, 2),
            "total_difference": round(total_diff, 2),
            "percentage_difference": round(pct_diff, 2),
            "formatted_difference": f"{total_diff:+,.2f}",
            "positive_count": int((diff_series > 0).sum()),
            "negative_count": int((diff_series < 0).sum())
        }

analysis_service = AnalysisService()
