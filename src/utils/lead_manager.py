import hashlib
import uuid
import os
from datetime import datetime
from typing import Dict, Any

import gspread
from google.oauth2.service_account import Credentials

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SPREADSHEET_ID = "1nOsGaFAvM2_pP-Sgu017SzfamV37baapvfehHnEZcbw"

# Resolve SA key path relative to this file → project root
_SA_KEY_PATH = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..",
        "corporte-athelete-leads-sa-key.json"
    )
)

# Only Sheets API is required — Drive API is NOT needed when opening by ID
_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

app_version = "2.0.0"


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------
def _connect():
    """
    Authenticate with the Service Account and return
    (metrics_sheet, marketing_sheet). Returns (None, None) on failure
    so the rest of the app degrades gracefully.
    """
    try:
        creds = Credentials.from_service_account_file(_SA_KEY_PATH, scopes=_SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        m_sheet  = spreadsheet.worksheet("leads_metrics")
        mk_sheet = spreadsheet.worksheet("leads_marketing")
        print("[lead_manager] Connected to Google Sheets successfully.")
        return m_sheet, mk_sheet
    except Exception as exc:
        print(f"[lead_manager] Google Sheets connection failed: {exc}")
        return None, None


# Module-level singletons — accessed directly by app.py
metrics_sheet, marketing_sheet = _connect()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------
def _hash_email(email: str) -> str:
    if not email:
        return ""
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

#deduplication fix

def save_marketing_lead(email: str, source: str = "benchmark") -> bool:
    """
    Saves a marketing lead to the leads_marketing sheet.
    Includes deduplication to prevent duplicate email entries.
    """
    if marketing_sheet is None:
        print("[lead_manager] marketing_sheet unavailable — lead not saved.")
        return False

    try:
        # Deduplication check: get all emails in column 1
        existing_emails = marketing_sheet.col_values(1)
        
        if email in existing_emails:
            # Email already exists, skip appending to keep data clean
            return False 
            
        # If not found, append the new row
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat()
        marketing_sheet.append_row([email, source, timestamp])
        return True
        
    except Exception as e:
        print(f"Error saving marketing lead: {e}")
        return False


def save_assessment(email: str, metrics_data: Dict[str, Any]) -> str:
    """
    Append one row to leads_metrics and (if email is given) save the
    marketing lead.  Returns the generated assessment_id UUID.

    Column order matches the sheet header exactly:
    score | category | age | gender | work_hours | meetings_per_day |
    sleep_hours | stress_level | email_hash | timestamp | assessment_id |
    ai_generated | top_limiter | recommended_action | app_version |
    user_goal | job_role
    """
    assessment_id = str(uuid.uuid4())
    email_hash    = _hash_email(email)
    timestamp     = datetime.utcnow().isoformat()

    if email:
        save_marketing_lead(email)

    if metrics_sheet is None:
        print("[lead_manager] metrics_sheet unavailable — assessment not persisted.")
        return assessment_id

    row_payload = [
        metrics_data.get("score"),                   # A  score
        metrics_data.get("category"),                # B  category
        metrics_data.get("age"),                     # C  age
        metrics_data.get("gender"),                  # D  gender
        metrics_data.get("work_hours"),              # E  work_hours
        metrics_data.get("meetings_per_day"),        # F  meetings_per_day
        metrics_data.get("sleep_hours"),             # G  sleep_hours
        metrics_data.get("stress_level"),            # H  stress_level
        email_hash,                                  # I  email_hash
        timestamp,                                   # J  timestamp
        assessment_id,                               # K  assessment_id
        False,                                       # L  ai_generated
        metrics_data.get("top_limiter", ""),         # M  top_limiter
        metrics_data.get("recommended_action", ""),  # N  recommended_action
        app_version,                                 # O  app_version
        metrics_data.get("user_goal", ""),           # P  user_goal
        metrics_data.get("job_role", ""),            # Q  job_role
    ]

    try:
        metrics_sheet.append_row(row_payload, value_input_option="USER_ENTERED")
    except Exception as exc:
        print(f"[lead_manager] Failed to append assessment row: {exc}")

    return assessment_id


def update_ai_response(assessment_id: str, ai_response_text: str) -> bool:
    """
    Mark the assessment row as AI-generated (column L = ai_generated).
    Returns True on success, False otherwise.
    """
    if metrics_sheet is None:
        return False
    try:
        cell = metrics_sheet.find(assessment_id, in_column=11)  # K = assessment_id
        if not cell:
            return False
        # Column L (index 12) = ai_generated flag
        metrics_sheet.update_cell(cell.row, 12, True)
        return True
    except Exception as exc:
        print(f"[lead_manager] Failed to update AI response flag: {exc}")
        return False


def calculate_score_percentile(score: int) -> int:
    from config import settings
    avg = settings.BENCHMARK_AVG_SCORE
    if score > avg:
        return min(99, 50 + int((score - avg) * 1.1))
    else:
        return max(1, 50 - int((avg - score) * 1.1))


def get_leads_snapshot(n: int) -> list:
    """Return up to n data rows from leads_metrics (excludes header)."""
    if metrics_sheet is None:
        return []
    try:
        all_rows = metrics_sheet.get_all_values()
        return all_rows[1 : n + 1]  # skip header row
    except Exception as exc:
        print(f"[lead_manager] Failed to fetch leads snapshot: {exc}")
        return []