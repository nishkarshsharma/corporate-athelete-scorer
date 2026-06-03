import os
import pandas as pd
from datetime import datetime
from config import settings

def save_lead(lead_data: dict) -> bool:
    """
    Saves user metrics and scoring information.
    Currently appends to a local CSV file. In a corporate environment,
    this can be replaced with a database transaction or a BigQuery insert.
    """
    try:
        csv_path = settings.LEAD_CSV_PATH
        
        # Ensure parent directory exists
        parent_dir = os.path.dirname(csv_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
            
        # Add timestamp if not present
        if "timestamp" not in lead_data:
            lead_data["timestamp"] = datetime.now().isoformat()
            
        df_new = pd.DataFrame([lead_data])
        
        if not os.path.exists(csv_path):
            df_new.to_csv(csv_path, index=False)
        else:
            df_new.to_csv(csv_path, mode='a', header=False, index=False)
        return True
    except Exception as e:
        # Logging error in enterprise environment
        print(f"Error saving lead: {e}")
        return False

def get_leads_snapshot(n: int = 5) -> pd.DataFrame:
    """
    Returns the latest n leads registered in the system.
    """
    csv_path = settings.LEAD_CSV_PATH
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(csv_path)
        return df.tail(n)
    except Exception:
        return pd.DataFrame()

def calculate_score_percentile(score: int) -> int:
    """
    Calculates the percentile ranking relative to the corporate benchmark.
    """
    avg = settings.BENCHMARK_AVG_SCORE
    std = settings.BENCHMARK_STD_DEV
    
    try:
        import scipy.stats as st_stats
        percentile = int(round(st_stats.norm.cdf(score, loc=avg, scale=std) * 100))
    except ImportError:
        # Robust fallback using normal-like scaling if scipy is missing
        if score > avg:
            percentile = min(99, 50 + int((score - avg) * 1.1))
        else:
            percentile = max(1, 50 - int((avg - score) * 1.1))
            
    return min(99, max(1, percentile))
