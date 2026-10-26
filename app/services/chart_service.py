import os
import uuid
import base64
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from app.config import settings

# Modern clean styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

class ChartService:
    @staticmethod
    def generate_chart(
        df: pd.DataFrame,
        chart_type: str,
        x_col: str,
        y_col: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates bar, line, pie, or scatter charts from dataframe data,
        saves to static charts folder, and returns relative URL and base64 string.
        """
        chart_type = chart_type.lower().strip()
        if chart_type not in ["bar", "line", "pie", "scatter", "hist"]:
            chart_type = "bar"

        # Unique filename
        filename = f"chart_{chart_type}_{uuid.uuid4().hex[:10]}.png"
        filepath = os.path.join(settings.CHARTS_DIR, filename)
        
        fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150)
        
        # Color palette
        palette = sns.color_palette("mako", 10)

        clean_title = title or f"{chart_type.capitalize()} Chart: {x_col}" + (f" vs {y_col}" if y_col else "")

        if chart_type == "bar":
            ChartService._render_bar(df, x_col, y_col, ax, palette)
        elif chart_type == "line":
            ChartService._render_line(df, x_col, y_col, ax, palette)
        elif chart_type == "pie":
            ChartService._render_pie(df, x_col, y_col, ax)
        elif chart_type == "scatter":
            ChartService._render_scatter(df, x_col, y_col, ax)
        elif chart_type == "hist":
            ChartService._render_hist(df, x_col, ax, palette)

        ax.set_title(clean_title, fontsize=14, fontweight="bold", pad=15, color="#1E293B")
        fig.tight_layout()
        fig.savefig(filepath, format="png", bbox_inches="tight")
        plt.close(fig)

        # Base64 string for direct rendering in UI without network delay
        with open(filepath, "rb") as img_file:
            b64_str = base64.b64encode(img_file.read()).decode('utf-8')
            b64_uri = f"data:image/png;base64,{b64_str}"

        rel_url = f"/static/charts/{filename}"
        return {
            "chart_type": chart_type,
            "filename": filename,
            "filepath": filepath,
            "url": rel_url,
            "base64_uri": b64_uri,
            "title": clean_title
        }

    @staticmethod
    def _render_bar(df: pd.DataFrame, x_col: str, y_col: Optional[str], ax, palette):
        if y_col and y_col in df.columns:
            plot_df = df.copy()
            plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors='coerce')
            grouped = plot_df.groupby(x_col)[y_col].sum().reset_index()
            grouped = grouped.sort_values(by=y_col, ascending=False).head(15)
            
            bars = ax.bar(grouped[x_col].astype(str), grouped[y_col], color="#800020", edgecolor="#5a0017", width=0.6)
            ax.set_ylabel(y_col, fontsize=11, fontweight="bold", color="#334155")
            
            # Value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:,.0f}",
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9, color="#1E293B")
        else:
            counts = df[x_col].value_counts().head(15)
            ax.bar(counts.index.astype(str), counts.values, color="#9b1137", edgecolor="#800020", width=0.6)
            ax.set_ylabel("Count", fontsize=11, fontweight="bold", color="#334155")

        ax.set_xlabel(x_col, fontsize=11, fontweight="bold", color="#334155")
        ax.tick_params(axis='x', rotation=35)

    @staticmethod
    def _render_line(df: pd.DataFrame, x_col: str, y_col: Optional[str], ax, palette):
        plot_df = df.copy()
        if y_col and y_col in plot_df.columns:
            plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors='coerce')
            
            # If x_col looks like date, sort chronologically
            try:
                plot_df['_dt'] = pd.to_datetime(plot_df[x_col], errors='coerce')
                plot_df = plot_df.dropna(subset=['_dt'])
                # Group by month or date
                grouped = plot_df.groupby(plot_df['_dt'].dt.strftime('%Y-%m'))[y_col].sum().reset_index()
                ax.plot(grouped['_dt'], grouped[y_col], marker='o', linewidth=2.5, color="#800020", markersize=6)
                ax.set_xlabel("Month", fontsize=11, fontweight="bold", color="#334155")
            except Exception:
                grouped = plot_df.groupby(x_col)[y_col].sum().reset_index()
                ax.plot(grouped[x_col].astype(str), grouped[y_col], marker='o', linewidth=2.5, color="#800020")
                ax.set_xlabel(x_col, fontsize=11, fontweight="bold", color="#334155")
                
            ax.set_ylabel(y_col, fontsize=11, fontweight="bold", color="#334155")
            ax.tick_params(axis='x', rotation=40)
        else:
            counts = plot_df[x_col].value_counts().sort_index()
            ax.plot(counts.index.astype(str), counts.values, marker='s', linewidth=2, color="#800020")
            ax.set_ylabel("Count", fontsize=11, fontweight="bold", color="#334155")

    @staticmethod
    def _render_pie(df: pd.DataFrame, x_col: str, y_col: Optional[str], ax):
        plot_df = df.copy()
        if y_col and y_col in plot_df.columns:
            plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors='coerce')
            grouped = plot_df.groupby(x_col)[y_col].sum().reset_index()
            grouped = grouped.sort_values(by=y_col, ascending=False).head(8)
            labels = grouped[x_col].astype(str)
            values = grouped[y_col]
        else:
            counts = plot_df[x_col].value_counts().head(8)
            labels = counts.index.astype(str)
            values = counts.values

        colors = sns.color_palette("pastel", len(labels))
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct='%1.1f%%',
            startangle=140, colors=colors,
            wedgeprops=dict(width=0.6, edgecolor='w', linewidth=2)
        )
        for autotext in autotexts:
            autotext.set_color('#1E293B')
            autotext.set_fontweight('bold')

    @staticmethod
    def _render_scatter(df: pd.DataFrame, x_col: str, y_col: Optional[str], ax):
        plot_df = df.copy()
        if not y_col or y_col not in plot_df.columns:
            # pick second numeric column
            num_cols = [c for c in plot_df.columns if pd.api.types.is_numeric_dtype(plot_df[c]) and c != x_col]
            y_col = num_cols[0] if num_cols else x_col

        x_vals = pd.to_numeric(plot_df[x_col], errors='coerce')
        y_vals = pd.to_numeric(plot_df[y_col], errors='coerce')
        
        ax.scatter(x_vals, y_vals, alpha=0.7, color="#6366F1", edgecolors="#4338CA", s=60)
        ax.set_xlabel(x_col, fontsize=11, fontweight="bold", color="#334155")
        ax.set_ylabel(y_col, fontsize=11, fontweight="bold", color="#334155")

    @staticmethod
    def _render_hist(df: pd.DataFrame, x_col: str, ax, palette):
        x_vals = pd.to_numeric(df[x_col], errors='coerce').dropna()
        ax.hist(x_vals, bins=15, color="#10B981", edgecolor="#059669", alpha=0.85)
        ax.set_xlabel(x_col, fontsize=11, fontweight="bold", color="#334155")
        ax.set_ylabel("Frequency", fontsize=11, fontweight="bold", color="#334155")

chart_service = ChartService()
