import os
import streamlit as st
from huggingface_hub import InferenceClient
from config import settings
from src.score_engine import get_category, detect_limiters, calculate_score_details

def generate_fallback_coaching(score: int, category: str, limiters: list) -> str:
    """
    Generates a high-quality rules-based coaching markdown when Hugging Face Token is unavailable.
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
*(Note: To unlock fully personalized, generative AI-driven coaching insights from open-source foundational models, please provide your Hugging Face Token in the sidebar).*
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
    Retrieves the coaching report using central configurations and Hugging Face prompt presets.
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
    
    # Secure Token Retrieval (Safely wraps st.secrets to prevent hard file-missing crashes)
    try:
        st_token = st.secrets.get("HF_TOKEN") if st.secrets else None
    except Exception:
        st_token = None

    key = (
        api_key 
        or st_token 
        or os.environ.get(getattr(settings, "HF_TOKEN_ENV_VAR", "HF_TOKEN"))
    )

    try:
        # Standardized on a stable shared-infrastructure configuration fallback (Meta Llama 3.1)
        # To swap to a DeepSeek setup, change HF_MODEL in config/settings.py to "deepseek-ai/DeepSeek-V3"
        model_name = getattr(settings, "HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
        client = InferenceClient(model=model_name, token=key)
        
        # Parse score limiters for the prompt context
        limiters_text = "\n".join([
            f"- {lim['name']} (Score impact: -{round(lim['score_impact'], 1)} pts, Current: {lim['stat']})"
            for lim in limiters
        ]) if limiters else "None. Good overall balance."
            
        system_instruction = settings.DEFAULT_SYSTEM_INSTRUCTION
        
        prompt_content = settings.DEFAULT_COACHING_PROMPT.format(
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
            limiters_text=limiters_text
        )
        
        # Conversational payload structures grounded directly to official Meta/DeepSeek templates
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt_content}
            ],
            max_tokens=1024,
            temperature=0.7
        )
        
        return {
            "is_ai": True,
            "content": response.choices[0].message.content
        }
        
    except Exception as e:
        fallback_content = generate_fallback_coaching(score, category, limiters)
        error_msg = f"\n\n*(Note: Hugging Face Inference API failed with: {str(e)}. Displaying rules-based fallback).* "
        return {
            "is_ai": False,
            "content": fallback_content + error_msg
        }