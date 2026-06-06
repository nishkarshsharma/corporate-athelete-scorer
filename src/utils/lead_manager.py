import os
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import hashlib
from config import settings

try:
    IS_LOCAL = "connections" not in st.secrets
except st.errors.StreamlitSecretNotFoundError:
    IS_LOCAL = True  # Safely default to True if no secrets file exists locally

if not IS_LOCAL:
    from streamlit_gsheets import GSheetsConnection
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        IS_LOCAL = True  # Fallback gracefully if connection config fails

def _hash_email(email: str) -> str:
    """
    Cleans and hashes an email address using SHA-256 to ensure data anonymity.
    """
    if not email:
        return ""
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()

def save_lead(lead_data: dict) -> bool:
    """
    Splits data into decoupled tracks: anonymized user metrics in tab 1,
    and raw email details in tab 2 for standalone marketing functions.
    """
    try:
        timestamp = datetime.now().isoformat()
        raw_email = lead_data.get("email", "").strip()
        
        if not raw_email:
            print("Error saving lead: Email is required.")
            return False

        # --- PREPARE DATASET 1: ANONYMOUS METRICS ---
        metrics_payload = lead_data.copy()
        metrics_payload["email_hash"] = _hash_email(raw_email)
        metrics_payload["timestamp"] = timestamp
        # Strip out personal identifier
        if "email" in metrics_payload:
            del metrics_payload["email"]
            
        df_metrics_new = pd.DataFrame([metrics_payload])

        # --- PREPARE DATASET 2: ISOLATED MARKETING LIST ---
        marketing_payload = {
            "email": raw_email,
            "timestamp": timestamp
        }
        df_marketing_new = pd.DataFrame([marketing_payload])

        # --- WORK WITH TAB 1: leads_metrics ---h
        try:
            # worksheet parameter targets the specific tab
            existing_metrics = conn.read(worksheet="leads_metrics", ttl=0)
        except Exception:
            existing_metrics = pd.DataFrame()

        if existing_metrics.empty:
            updated_metrics = df_metrics_new
        else:
            updated_metrics = pd.concat([existing_metrics, df_metrics_new], ignore_index=True)
        
        conn.update(worksheet="leads_metrics", data=updated_metrics)

        # --- WORK WITH TAB 2: leads_marketing ---
        try:
            existing_marketing = conn.read(worksheet="leads_marketing", ttl=0)
        except Exception:
            existing_marketing = pd.DataFrame()

        if existing_marketing.empty:
            updated_marketing = df_marketing_new
        else:
            updated_marketing = pd.concat([existing_marketing, df_marketing_new], ignore_index=True)
            
        conn.update(worksheet="leads_marketing", data=updated_marketing)

        return True
        
    except Exception as e:
        print(f"Error executing tokenized save routine: {e}")
        return False

def get_leads_snapshot(n: int = 5) -> pd.DataFrame:
    """
    Returns the latest n entries from the marketing email track.
    """
    try:
        df = conn.read(worksheet="leads_metrics", ttl=0)
        if df.empty:
            return pd.DataFrame()
        return df.tail(n)
    except Exception as e:
        print(f"Error fetching leads snapshot: {e}")
        return pd.DataFrame()

def calculate_score_percentile(score: int) -> int:
    """
    Calculates the percentile ranking relative to the corporate benchmark.
    """
    avg = settings.BENCHMARK_AVG_SCORE
    st_dev = settings.BENCHMARK_STD_DEV
    
    try:
        import scipy.stats as st_stats
        percentile = int(round(st_stats.norm.cdf(score, loc=avg, scale=st_dev) * 100))
    except ImportError:
        if score > avg:
            percentile = min(99, 50 + int((score - avg) * 1.1))
        else:
            percentile = max(1, 50 - int((avg - score) * 1.1))
            
    return min(99, max(1, percentile))