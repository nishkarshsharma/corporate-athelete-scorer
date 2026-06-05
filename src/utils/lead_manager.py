import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Initialize the Google Sheets Connection
# It automatically picks up the credentials from your Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def save_lead_to_sheets(email, score, category, age, gender, work_hours, meetings_per_day, sleep_hours, stress_level):
    """
    Appends a new lead row directly into the connected Google Sheet
    using your exact metric headers.
    """
    try:
        # 1. Fetch current data from the Google Sheet (ttl=0 ensures fresh data without caching)
        existing_data = conn.read(ttl=0)
    except Exception:
        # Fallback if the Google Sheet is entirely empty/new
        existing_data = pd.DataFrame()

    # 2. Build the new lead row structured with your exact data parameters
    new_lead = pd.DataFrame([{
        "email": email,
        "score": score,
        "category": category,
        "age": age,
        "gender": gender,
        "work_hours": work_hours,
        "meetings_per_day": meetings_per_day,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])

    # 3. Append the new row to existing entries
    updated_data = pd.concat([existing_data, new_lead], ignore_index=True)

    # 4. Save and overwrite the sheet live on Google Drive
    conn.update(data=updated_data)
    st.success("Lead saved successfully to Google Sheets!")