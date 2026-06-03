import os
from google import genai
from google.genai import types
from config import settings
from src.score_engine import get_category, detect_limiters, calculate_score_details

def generate_fallback_coaching(score: int, category: str, limiters: list) -> str:
    """
    Generates a high-quality rules-based coaching markdown when Gemini API key is unavailable.
    """
    if not limiters:
        bottleneck = "General lifestyle balance is good. Focus on maintaining consistency."
        protocol = (
            "- **Daily Consistency:** Maintain current sleep and active patterns.\n"
            "- **Stress Checks:** Do a weekly stress check-in to ensure cognitive fatigue is low.\n"
            "- **Progressive Overload:** Try adding 1 extra training day or slightly increasing intensity."
        )
    else:
        primary = limiters[0]
        bottleneck = f"**{primary['name']}** (Current: {primary['stat']}). It drains your energy by up to {int(primary['score_impact'])}% of your potential score."
        
        protocol_steps = []
        for i, lim in enumerate(limiters[:3]):
            step_num = i + 1
            protocol_steps.append(f"{step_num}. **Address {lim['name']}**: {lim['recommendation']}")
        protocol = "\n".join(protocol_steps)

    markdown = f"""### 🚀 The Corporate Bottleneck
{bottleneck}

### 📅 The 1-Week Micro-Habit Protocol
Here is your rules-based, tactical action plan for the week:
{protocol}

### 💡 Coach's Perspective
*Your energy is a strategic business asset. Small, compounding changes to your daily physiology will yield exponential career gains. Treat recovery like a mission-critical deliverable.*

---
*(Note: To unlock fully personalized, generative AI-driven coaching insights from Gemini Flash, please provide your Gemini API key in the sidebar).*
"""
    return markdown

def get_coaching_report(
    age: int,
    weight: float,
    height: float,
    work_hours: float,
    meetings_per_day: float,
    commute_hours: float,
    sleep_hours: float,
    travel_days: float,
    training_days: float,
    stress_level: float,
    gender: str = "Male",
    api_key: str = None
) -> dict:
    """
    Retrieves the coaching report using central configurations and prompt presets.
    """
    details = calculate_score_details(
        age, weight, height, work_hours, meetings_per_day, commute_hours,
        sleep_hours, travel_days, training_days, stress_level, gender
    )
    score = details["total_score"]
    category = get_category(score)
    limiters = detect_limiters(
        details, sleep_hours, meetings_per_day, commute_hours,
        work_hours, travel_days, training_days, stress_level
    )
    
    # Read API Key
    key = api_key or os.environ.get(settings.GEMINI_API_KEY_ENV_VAR)
    
    if not key:
        return {
            "is_ai": False,
            "content": generate_fallback_coaching(score, category, limiters)
        }
        
    try:
        client = genai.Client(api_key=key)
        
        limiters_text = ""
        for lim in limiters:
            limiters_text += f"- {lim['name']} (Score impact: -{round(lim['score_impact'], 1)} pts, Current: {lim['stat']})\n"
            
        system_instruction = settings.DEFAULT_SYSTEM_INSTRUCTION
        
        prompt = settings.DEFAULT_COACHING_PROMPT.format(
            score=score,
            category=category,
            age=age,
            gender=gender,
            bmi=details['bmi'],
            weight=weight,
            height=height,
            work_hours=work_hours,
            meetings_per_day=meetings_per_day,
            commute_hours=commute_hours,
            sleep_hours=sleep_hours,
            travel_days=travel_days,
            training_days=training_days,
            stress_level=stress_level,
            limiters_text=limiters_text if limiters_text else "None. Good overall balance."
        )
        
        response = client.models.generate_content(
            model=settings.DEFAULT_GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            )
        )
        
        return {
            "is_ai": True,
            "content": response.text
        }
        
    except Exception as e:
        fallback_content = generate_fallback_coaching(score, category, limiters)
        error_msg = f"\n\n*(Note: Gemini API Call failed with: {str(e)}. Displaying rules-based fallback).* "
        return {
            "is_ai": False,
            "content": fallback_content + error_msg
        }
