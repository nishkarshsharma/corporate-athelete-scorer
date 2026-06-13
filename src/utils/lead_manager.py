import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class DummySheet:
    def find(self, *args, **kwargs):
        return None
    def update_cell(self, *args, **kwargs):
        pass
    def append_row(self, *args, **kwargs):
        pass
    def update(self, *args, **kwargs):
        pass

metrics_sheet = DummySheet()
marketing_sheet = DummySheet()
app_version = "2.0.0"

def _hash_email(email: str) -> str:
    if not email:
        return ""
    return hashlib.sha256(email.strip().lower().encode('utf-8')).hexdigest()

def save_marketing_lead(email: str):
    if email:
        timestamp = datetime.utcnow().isoformat()
        marketing_sheet.append_row([email.strip().lower(), timestamp])

def save_assessment(email: str, metrics_data: Dict[str, Any]) -> str:
    assessment_id = str(uuid.uuid4())
    email_hash = _hash_email(email)
    timestamp = datetime.utcnow().isoformat()

    if email:
        save_marketing_lead(email)

    row_payload = [
        metrics_data.get("score"),
        metrics_data.get("category"),
        metrics_data.get("age"),
        metrics_data.get("gender"),
        metrics_data.get("work_hours"),
        metrics_data.get("meetings_per_day"),
        metrics_data.get("sleep_hours"),
        metrics_data.get("stress_level"),
        email_hash,
        timestamp,
        assessment_id,
        False,
        "",
        metrics_data.get("top_limiter", ""),
        metrics_data.get("recommended_action", ""),
        app_version,
        metrics_data.get("user_goal", ""),
        metrics_data.get("job_role", "")
    ]
    metrics_sheet.append_row(row_payload)
    return assessment_id

def update_ai_response(assessment_id: str, ai_response_text: str) -> bool:
    try:
        cell = metrics_sheet.find(assessment_id, in_column=11)
        if not cell:
            return False
        row_index = cell.row
        update_range = f"L{row_index}:M{row_index}"
        metrics_sheet.update(update_range, [[True, ai_response_text]])
        return True
    except Exception:
        return False

def calculate_score_percentile(score: int) -> int:
    from config import settings
    avg = settings.BENCHMARK_AVG_SCORE
    if score > avg:
        return min(99, 50 + int((score - avg) * 1.1))
    else:
        return max(1, 50 - int((avg - score) * 1.1))

def get_leads_snapshot(n: int) -> list:
    return []