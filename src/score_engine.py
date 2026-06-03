import math
from config import settings

def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculates Body Mass Index (BMI).
    weight: Weight in kg
    height: Height in cm
    """
    if height <= 0 or weight <= 0:
        return 22.0  # Fallback to normal BMI
    return weight / ((height / 100) ** 2)

def calculate_score_details(
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
    gender: str = "Male"
) -> dict:
    """
    Calculates detailed score components and total score.
    Returns a dictionary of individual component scores and the total score.
    """
    # 1. Sleep Score (Max 25)
    if sleep_hours >= 8:
        sleep_score = 25.0
    elif sleep_hours >= 7:
        sleep_score = 20.0 + (sleep_hours - 7.0) * 5.0
    elif sleep_hours >= 6:
        sleep_score = 12.0 + (sleep_hours - 6.0) * 8.0
    elif sleep_hours >= 5:
        sleep_score = 5.0 + (sleep_hours - 5.0) * 7.0
    else:
        sleep_score = max(0.0, sleep_hours * 1.0)
    
    # 2. Work & Meetings (Max 20: 10 for work, 10 for meetings)
    # Work Hours Score (Max 10)
    if work_hours <= 40:
        work_score = 10.0
    elif work_hours <= 50:
        work_score = 10.0 - (work_hours - 40.0) * 0.4
    elif work_hours <= 60:
        work_score = 6.0 - (work_hours - 50.0) * 0.4
    else:
        work_score = max(0.0, 2.0 - (work_hours - 60.0) * 0.1)

    # Meetings Score (Max 10)
    if meetings_per_day <= 2:
        meetings_score = 10.0
    elif meetings_per_day <= 5:
        meetings_score = 10.0 - (meetings_per_day - 2.0) * 1.5
    elif meetings_per_day <= 8:
        meetings_score = 5.5 - (meetings_per_day - 5.0) * 1.5
    else:
        meetings_score = max(0.0, 1.0 - (meetings_per_day - 8.0) * 0.2)
        
    work_meetings_score = work_score + meetings_score

    # 3. Physical Activity & Commute (Max 25: 15 for training, 10 for commute)
    # Training Score (Max 15)
    training_days_clamped = max(0.0, min(7.0, training_days))
    if training_days_clamped >= 4:
        training_score = 15.0
    elif training_days_clamped == 3:
        training_score = 12.0
    elif training_days_clamped == 2:
        training_score = 8.0
    elif training_days_clamped == 1:
        training_score = 4.0
    else:
        training_score = 0.0

    # Commute Score (Max 10)
    if commute_hours <= 0.5:
        commute_score = 10.0
    elif commute_hours <= 1.5:
        commute_score = 10.0 - (commute_hours - 0.5) * 4.0
    elif commute_hours <= 2.5:
        commute_score = 6.0 - (commute_hours - 1.5) * 4.0
    else:
        commute_score = max(0.0, 2.0 - (commute_hours - 2.5) * 1.0)
        
    physical_activity_score = training_score + commute_score

    # 4. Stress & Travel (Max 20: 10 for stress, 10 for travel)
    # Stress Score (Max 10)
    stress_score = max(0.0, min(10.0, 11.0 - stress_level))

    # Travel Score (Max 10)
    if travel_days <= 2:
        travel_score = 10.0
    elif travel_days <= 5:
        travel_score = 10.0 - (travel_days - 2.0) * 1.0
    elif travel_days <= 10:
        travel_score = 7.0 - (travel_days - 5.0) * 0.8
    else:
        travel_score = max(0.0, 3.0 - (travel_days - 10.0) * 0.2)
        
    stress_travel_score = stress_score + travel_score

    # 5. Biometrics Score (Max 10)
    bmi = calculate_bmi(weight, height)
    if 18.5 <= bmi <= 24.9:
        biometrics_score = 10.0
    elif 25.0 <= bmi <= 29.9:
        biometrics_score = max(5.0, 10.0 - (bmi - 25.0) * 1.0)
    elif bmi >= 30.0:
        biometrics_score = max(0.0, 5.0 - (bmi - 30.0) * 0.5)
    else:
        biometrics_score = max(2.0, 10.0 - (18.5 - bmi) * 1.5)

    # Sum components
    total_score = sleep_score + work_meetings_score + physical_activity_score + stress_travel_score + biometrics_score
    total_score = max(0.0, min(100.0, total_score))

    return {
        "sleep_score": round(sleep_score, 1),
        "work_score": round(work_score, 1),
        "meetings_score": round(meetings_score, 1),
        "work_meetings_score": round(work_meetings_score, 1),
        "training_score": round(training_score, 1),
        "commute_score": round(commute_score, 1),
        "physical_activity_score": round(physical_activity_score, 1),
        "stress_score": round(stress_score, 1),
        "travel_score": round(travel_score, 1),
        "stress_travel_score": round(stress_travel_score, 1),
        "biometrics_score": round(biometrics_score, 1),
        "bmi": round(bmi, 1),
        "total_score": int(round(total_score))
    }

def get_category(score: int) -> str:
    """
    Maps score to category.
    """
    if score >= 81:
        return "Elite Corporate Athlete"
    elif score >= 61:
        return "Weekend Warrior"
    elif score >= 41:
        return "Sedentary Corporate Warrior"
    else:
        return "Executive Burnout Risk"

def calculate_fitness_potential(
    score: int,
    gender: str,
    age: int,
    weight: float,
    height: float,
    training_days: float,
    meetings_per_day: float,
    commute_hours: float,
    work_hours: float
) -> dict:
    """
    Predicts body fat range, daily step goals, and target training frequency.
    """
    bmi = calculate_bmi(weight, height)
    
    # Body Fat projection
    if gender.lower() == "male":
        base_bf = 15.0
        min_bf, max_bf = 8.0, 35.0
    elif gender.lower() == "female":
        base_bf = 22.0
        min_bf, max_bf = 16.0, 42.0
    else:
        base_bf = 18.5
        min_bf, max_bf = 12.0, 38.0
        
    bf_penalty = (100 - score) * 0.2
    
    if bmi > 25.0:
        bf_penalty += (bmi - 25.0) * 1.2
    elif bmi < 18.5:
        bf_penalty -= (18.5 - bmi) * 1.0

    training_bonus = training_days * 0.8
    predicted_bf = base_bf + bf_penalty - training_bonus
    predicted_bf = max(min_bf, min(max_bf, predicted_bf))
    
    bf_low = round(predicted_bf - 1.5, 1)
    bf_high = round(predicted_bf + 1.5, 1)
    bf_low = max(min_bf, bf_low)
    bf_high = min(max_bf, bf_high)
    
    # Steps target/day
    base_steps = 10000.0
    meeting_penalty = meetings_per_day * 400.0
    commute_penalty = commute_hours * 600.0
    work_penalty = 500.0 if work_hours > 50 else 0.0
    training_boost = training_days * 800.0
    
    predicted_steps = base_steps - meeting_penalty - commute_penalty - work_penalty + training_boost
    predicted_steps = max(4000.0, min(12000.0, predicted_steps))
    steps_target = int(math.ceil(predicted_steps / 500.0) * 500)
    
    if work_hours > 60:
        recommended_gym = 3
    elif work_hours > 50:
        recommended_gym = 3 if training_days < 3 else int(min(training_days, 4))
    else:
        recommended_gym = max(int(training_days), 3)
        
    recommended_gym = max(1, min(recommended_gym, 5))

    return {
        "body_fat_range": f"{bf_low}% - {bf_high}%",
        "steps_target": steps_target,
        "gym_sessions_target": recommended_gym
    }

def detect_limiters(
    score_details: dict,
    sleep_hours: float,
    meetings_per_day: float,
    commute_hours: float,
    work_hours: float,
    travel_days: float,
    training_days: float,
    stress_level: float
) -> list:
    """
    Identifies components causing the biggest score drain.
    """
    limiters = []
    
    # 1. Sleep
    sleep_pct = score_details["sleep_score"] / 25.0
    if sleep_hours < 7.0:
        limiters.append({
            "name": "Sleep Deficit",
            "score_impact": 25.0 - score_details["sleep_score"],
            "pct": sleep_pct,
            "recommendation": f"Increase daily sleep by {int((7.5 - sleep_hours)*60)} mins to improve memory, stress tolerance, and recovery.",
            "stat": f"{sleep_hours} hrs/day"
        })
        
    # 2. Work Hours
    work_pct = score_details["work_score"] / 10.0
    if work_hours > 45:
        limiters.append({
            "name": "Excessive Work Hours",
            "score_impact": 10.0 - score_details["work_score"],
            "pct": work_pct,
            "recommendation": "Establish strict 'hard stops' at the end of the day. Block focus times to finish work within standard hours.",
            "stat": f"{work_hours} hrs/week"
        })
        
    # 3. Meetings
    meeting_pct = score_details["meetings_score"] / 10.0
    if meetings_per_day > 4:
        limiters.append({
            "name": "Meeting Fatigue",
            "score_impact": 10.0 - score_details["meetings_score"],
            "pct": meeting_pct,
            "recommendation": "Decline non-essential meetings or shorten 30-min meetings to 20-mins. Block 1-hour focus slots daily.",
            "stat": f"{meetings_per_day} meetings/day"
        })
        
    # 4. Stress
    stress_pct = score_details["stress_score"] / 10.0
    if stress_level > 6:
        limiters.append({
            "name": "High Chronic Stress",
            "score_impact": 10.0 - score_details["stress_score"],
            "pct": stress_pct,
            "recommendation": "Incorporate a 5-minute deep breathing or mindfulness protocol twice a day (e.g. before start and at lunch).",
            "stat": f"Level {stress_level}/10"
        })
        
    # 5. Travel
    travel_pct = score_details["travel_score"] / 10.0
    if travel_days > 4:
        limiters.append({
            "name": "Frequent Business Travel",
            "score_impact": 10.0 - score_details["travel_score"],
            "pct": travel_pct,
            "recommendation": "Optimize travel nutrition; carry high-protein snacks. Choose hotels with gym access or perform 20-min in-room bodyweight sessions.",
            "stat": f"{travel_days} days/month"
        })

    # 6. Physical Activity / Training
    training_pct = score_details["training_score"] / 15.0
    if training_days < 3:
        limiters.append({
            "name": "Sedentary Routine",
            "score_impact": 15.0 - score_details["training_score"],
            "pct": training_pct,
            "recommendation": "Aim for at least 3 exercise sessions per week (even 20-minute home workouts count). Incorporate desk mobility routines.",
            "stat": f"{training_days} training days/week"
        })
        
    # 7. Commute Time
    commute_pct = score_details["commute_score"] / 10.0
    if commute_hours > 1.0:
        limiters.append({
            "name": "Long Daily Commute",
            "score_impact": 10.0 - score_details["commute_score"],
            "pct": commute_pct,
            "recommendation": "Use commute time productively (e.g. audiobooks, educational podcasts) to reduce frustration. Incorporate walking if taking transit.",
            "stat": f"{commute_hours} hrs/day"
        })

    limiters.sort(key=lambda x: x["score_impact"], reverse=True)
    return limiters

def simulate_promotion(promotion_tier: str, current_metrics: dict) -> dict:
    """
    Simulates the impact of a promotion on the athlete's metrics and score.
    Uses promotion impacts defined in central config settings.
    """
    if promotion_tier not in settings.PROMOTION_IMPACTS:
        raise ValueError(f"Unknown promotion tier: {promotion_tier}")
        
    impact = settings.PROMOTION_IMPACTS[promotion_tier]
    
    simulated_metrics = {
        "age": current_metrics["age"],
        "weight": current_metrics["weight"],
        "height": current_metrics["height"],
        "gender": current_metrics.get("gender", "Male"),
        "work_hours": min(100.0, max(0.0, current_metrics["work_hours"] + impact["work_hours"])),
        "meetings_per_day": min(15.0, max(0.0, current_metrics["meetings_per_day"] + impact["meetings_per_day"])),
        "commute_hours": current_metrics["commute_hours"],
        "sleep_hours": min(12.0, max(3.0, current_metrics["sleep_hours"] + impact["sleep_hours"])),
        "travel_days": min(30.0, max(0.0, current_metrics["travel_days"] + impact["travel_days"])),
        "training_days": min(7.0, max(0.0, current_metrics["training_days"] + impact["training_days"])),
        "stress_level": min(10.0, max(1.0, current_metrics["stress_level"] + impact["stress_level"]))
    }
    
    simulated_details = calculate_score_details(**simulated_metrics)
    current_details = calculate_score_details(**current_metrics)
    
    current_potential = calculate_fitness_potential(
        current_details["total_score"],
        current_metrics.get("gender", "Male"),
        current_metrics["age"],
        current_metrics["weight"],
        current_metrics["height"],
        current_metrics["training_days"],
        current_metrics["meetings_per_day"],
        current_metrics["commute_hours"],
        current_metrics["work_hours"]
    )
    
    simulated_potential = calculate_fitness_potential(
        simulated_details["total_score"],
        simulated_metrics["gender"],
        simulated_metrics["age"],
        simulated_metrics["weight"],
        simulated_metrics["height"],
        simulated_metrics["training_days"],
        simulated_metrics["meetings_per_day"],
        simulated_metrics["commute_hours"],
        simulated_metrics["work_hours"]
    )
    
    return {
        "current_metrics": current_metrics,
        "simulated_metrics": simulated_metrics,
        "current_score": current_details["total_score"],
        "simulated_score": simulated_details["total_score"],
        "current_category": get_category(current_details["total_score"]),
        "simulated_category": get_category(simulated_details["total_score"]),
        "current_potential": current_potential,
        "simulated_potential": simulated_potential,
        "metric_deltas": {
            "work_hours": impact["work_hours"],
            "meetings_per_day": impact["meetings_per_day"],
            "stress_level": impact["stress_level"],
            "sleep_hours": impact["sleep_hours"],
            "travel_days": impact["travel_days"],
            "training_days": impact["training_days"]
        }
    }
