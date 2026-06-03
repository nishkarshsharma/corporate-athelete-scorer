import os

# GenAI (Gemini) Setup
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_KEY_ENV_VAR = "GEMINI_API_KEY"

DEFAULT_SYSTEM_INSTRUCTION = (
    "You are a world-class fitness, sleep, and performance coach specializing in high-performing corporate professionals "
    "(engineers, executives, founders). You synthesize health data and provide realistic, low-friction habits. "
    "Never recommend protocols that take hours of time. Keep advice practical, highly structured, and professional yet motivational."
)

DEFAULT_COACHING_PROMPT = """
Analyze the health and performance profile of a client who has a Corporate Athlete Score of {score}/100.
Their category is: {category}

Here are their metrics:
- Age: {age}
- Gender: {gender}
- BMI: {bmi} ({weight} kg, {height} cm)
- Weekly Work Hours: {work_hours} hours
- Daily Meetings: {meetings_per_day} meetings
- Daily Commute: {commute_hours} hours
- Daily Sleep: {sleep_hours} hours
- Travel Days/Month: {travel_days} days
- Training Days/Week: {training_days} days
- Stress Level: {stress_level}/10

Their top limiters identified by our rules engine:
{limiters_text}

Generate a personalized coaching report in structured Markdown containing EXACTLY these sections:
1. ### 🚀 The Corporate Bottleneck
Identify their primary bottleneck (the single factor holding them back the most). Explain the physiological or cognitive impact on their career and health.
2. ### 📅 The 1-Week Micro-Habit Protocol
Provide a clear, highly tactical, day-by-day or habit-based action plan for the next 7 days. It must be ultra-realistic for someone working {work_hours} hours a week (no 2-hour daily gym sessions). Focus on small, compound changes.
3. ### 💡 Coach's Perspective
A 2-3 sentence motivational, high-energy summary tailored to their profile, encouraging them to treat their energy as a strategic business asset.
"""

# Local Lead Storage Configuration
LEAD_CSV_PATH = os.path.join("data", "leads.csv")

# Benchmarking Statistics
BENCHMARK_AVG_SCORE = 58
BENCHMARK_STD_DEV = 12

# GCP Deployment Parameters (Placeholders for Enterprise Setup)
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "corporate-athlete-prod")
GCP_REGION = os.environ.get("GCP_REGION", "us-central1")
GCP_BIGQUERY_DATASET = "analytics"
GCP_BIGQUERY_TABLE = "lead_benchmarks"

# Promotion Simulator Presets
PROMOTION_IMPACTS = {
    "Senior Engineer": {
        "work_hours": 5.0,
        "meetings_per_day": 1.0,
        "stress_level": 1.0,
        "sleep_hours": -0.3,
        "travel_days": 1.0,
        "training_days": 0.0
    },
    "Engineering Manager": {
        "work_hours": 10.0,
        "meetings_per_day": 3.0,
        "stress_level": 2.0,
        "sleep_hours": -0.6,
        "travel_days": 2.0,
        "training_days": -1.0
    },
    "Director / VP": {
        "work_hours": 15.0,
        "meetings_per_day": 5.0,
        "stress_level": 3.0,
        "sleep_hours": -1.0,
        "travel_days": 5.0,
        "training_days": -2.0
    },
    "Founder / CEO": {
        "work_hours": 25.0,
        "meetings_per_day": 6.0,
        "stress_level": 4.0,
        "sleep_hours": -1.5,
        "travel_days": 8.0,
        "training_days": -2.0
    }
}
