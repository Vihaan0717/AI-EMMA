import pandas as pd
import numpy as np
import json
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger("AnalyticsTools")

class DataCruncher:
    """
    Core Analytics Engine for Atlas-X.
    Handles data ingestion, cleaning, and statistical synthesis.
    """
    
    @staticmethod
    def load_data(file_path: str) -> Optional[pd.DataFrame]:
        """Loads data from CSV, Excel, or JSON."""
        ext = Path(file_path).suffix.lower()
        try:
            if ext == '.csv':
                return pd.read_csv(file_path)
            elif ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
            elif ext == '.json':
                return pd.read_json(file_path)
            else:
                logger.error(f"Unsupported file format: {ext}")
                return None
        except Exception as e:
            logger.error(f"Failed to load data from {file_path}: {e}")
            return None

    @staticmethod
    def get_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """Generates high-level descriptive statistics."""
        summary = {
            "rows": len(df),
            "columns": list(df.columns),
            "numeric_summary": df.describe().to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
        }
        return summary

    @staticmethod
    def analyze_sales_trends(df: pd.DataFrame, date_col: str, sales_col: str) -> Dict[str, Any]:
        """Specifically analyzes sales growth and trends."""
        try:
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.sort_values(by=date_col)
            
            # Daily/Monthly aggregation
            df.set_index(date_col, inplace=True)
            monthly_sales = df[sales_col].resample('ME').sum()
            
            growth = monthly_sales.pct_change().fillna(0) * 100
            
            return {
                "total_sales": float(df[sales_col].sum()),
                "avg_monthly_sales": float(monthly_sales.mean()),
                "monthly_growth_rates": growth.to_dict(),
                "peak_month": str(monthly_sales.idxmax()),
                "trend": "increasing" if growth.mean() > 0 else "decreasing"
            }
        except Exception as e:
            return {"error": f"Sales analysis failed: {e}"}

    @staticmethod
    def identify_outliers(df: pd.DataFrame, column: str) -> List[Any]:
        """Detects anomalies in a specific metric."""
        if column not in df.columns:
            return []
        
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        return outliers.to_dict(orient='records')

def run_quick_analysis(file_path: str) -> str:
    """Convenience function for Atlas-X to get a quick snapshot of a file."""
    df = DataCruncher.load_data(file_path)
    if df is None:
        return "Error: Could not load data file."
    
    stats = DataCruncher.get_summary_stats(df)
    return json.dumps(stats, indent=2, default=str)
