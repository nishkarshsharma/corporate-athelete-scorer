import os
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from config import settings

# Initialize the Google Sheets Connection natively via Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

def save_lead(lead_data: dict) -> bool:
    """
    Saves user metrics and scoring information by appending data
    directly into your connected live Google Sheet.
    """
    try:
        # 1. Ensure timestamp exists in your payload
        if "timestamp" not in lead_data:
            lead_data["timestamp"] = datetime.now().isoformat()
            
        # Convert single dictionary lead info to a DataFrame
        df_new = pd.DataFrame([lead_data])
        
        try:
            # 2. Read current contents from the spreadsheet (no caching to stay live)
            existing_data = conn.read(ttl=0)
        except Exception:
            # Fallback if the Google Sheet has never been initialized or has no header
            existing_data = pd.DataFrame()

        # 3. Append the new lead entry dynamically
        if existing_data.empty:
            updated_data = df_new
        else:
            updated_data = pd.concat([existing_data, df_new], ignore_index=True)
        
        # 4. Upload and commit back up to Google Drive
        conn.update(data=updated_data)
        return True
        
    except Exception as e:
        print(f"Error saving lead to Google Sheets: {e}")
        return False

def get_leads_snapshot(n: int = 5) -> pd.DataFrame:
    """
    Returns the latest n leads registered directly from your Google Sheet.
    """
    try:
        # Read live data from the sheet
        df = conn.read(ttl=0)
        if df.empty:
            return pd.DataFrame()
        return df.tail(n)
    except Exception as e:
        print(f"Error fetching leads snapshot: {e}")
        return pd.DataFrame()

def calculate_score_percentile(score: int) -> int:
    """
    Calculates the percentile ranking relative to the corporate benchmark.
    Kept identical to original to ensure seamless app calculations.
    """
    avg = settings.BENCHMARK_AVG_SCORE
    st_dev = settings.BENCHMARK_STD_DEV
    
    try:
        import scipy.stats as st_stats
        percentile = int(round(st_stats.norm.cdf(score, loc=avg, scale=st_dev) * 100))
    except ImportError:
        # Robust fallback using normal-like scaling if scipy is missing
        if score > avg:
            percentile = min(99, 50 + int((score - avg) * 1.1))
        else:
            percentile = max(1, 50 - int((avg - score) * 1.1))
            
    return min(99, max(1, percentile))