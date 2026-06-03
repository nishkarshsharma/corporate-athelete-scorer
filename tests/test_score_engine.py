from src.score_engine import (
    calculate_bmi,
    calculate_score_details,
    get_category,
    calculate_fitness_potential,
    detect_limiters,
    simulate_promotion
)
from config.settings import PROMOTION_IMPACTS

# ----------------- BMI TESTS (3 scenarios) -----------------
def test_calculate_bmi_normal():
    assert round(calculate_bmi(75.0, 178.0), 1) == 23.7

def test_calculate_bmi_zero_height():
    # Fallback to normal BMI 22.0
    assert calculate_bmi(75.0, 0.0) == 22.0

def test_calculate_bmi_negative():
    assert calculate_bmi(-75.0, 180.0) == 22.0


# ----------------- SLEEP SCORE MONOTONICITY & VALUES (5 scenarios) -----------------
def test_sleep_score_max():
    details = calculate_score_details(30, 70, 175, 40, 2, 0, 8.5, 0, 4, 1)
    assert details["sleep_score"] == 25.0

def test_sleep_score_7_hours():
    details = calculate_score_details(30, 70, 175, 40, 2, 0, 7.0, 0, 4, 1)
    assert details["sleep_score"] == 20.0

def test_sleep_score_6_5_hours():
    details = calculate_score_details(30, 70, 175, 40, 2, 0, 6.5, 0, 4, 1)
    assert details["sleep_score"] == 16.0

def test_sleep_score_5_5_hours():
    details = calculate_score_details(30, 70, 175, 40, 2, 0, 5.5, 0, 4, 1)
    assert details["sleep_score"] == 8.5

def test_sleep_score_poor():
    details = calculate_score_details(30, 70, 175, 40, 2, 0, 4.0, 0, 4, 1)
    assert details["sleep_score"] == 4.0


# ----------------- WORK & MEETINGS SCORE (4 scenarios) -----------------
def test_work_hours_clamping():
    # 40 hours should give max score (10)
    details = calculate_score_details(30, 70, 175, 40, 2, 0.5, 8, 2, 4, 1)
    assert details["work_score"] == 10.0
    
    # 55 hours
    details_55 = calculate_score_details(30, 70, 175, 55, 2, 0.5, 8, 2, 4, 1)
    assert details_55["work_score"] == 4.0

def test_meetings_scoring():
    # 2 meetings -> 10.0
    details = calculate_score_details(30, 70, 175, 40, 2, 0.5, 8, 2, 4, 1)
    assert details["meetings_score"] == 10.0
    
    # 5 meetings -> 5.5
    details_5 = calculate_score_details(30, 70, 175, 40, 5, 0.5, 8, 2, 4, 1)
    assert details_5["meetings_score"] == 5.5


# ----------------- PHYSICAL ACTIVITY & COMMUTE (4 scenarios) -----------------
def test_training_days_scoring():
    # 4 days -> 15.0
    details_4 = calculate_score_details(30, 70, 175, 40, 2, 0.5, 8, 2, 4, 1)
    assert details_4["training_score"] == 15.0

    # 2 days -> 8.0
    details_2 = calculate_score_details(30, 70, 175, 40, 2, 0.5, 8, 2, 2, 1)
    assert details_2["training_score"] == 8.0

def test_commute_scoring():
    # 0.5 hrs -> 10.0
    details_short = calculate_score_details(30, 70, 175, 40, 2, 0.5, 8, 2, 4, 1)
    assert details_short["commute_score"] == 10.0

    # 2.0 hrs -> 4.0
    details_long = calculate_score_details(30, 70, 175, 40, 2, 2.0, 8, 2, 4, 1)
    assert details_long["commute_score"] == 4.0


# ----------------- STRESS & TRAVEL SCORE (3 scenarios) -----------------
def test_stress_scoring():
    # Stress level 1 -> 10.0 score
    details_low = calculate_score_details(30, 70, 175, 40, 2, 0.5, 8, 2, 4, 1)
    assert details_low["stress_score"] == 10.0

    # Stress level 7 -> 4.0 score
    details_high = calculate_score_details(30, 70, 175, 40, 2, 0.5, 8, 2, 4, 7)
    assert details_high["stress_score"] == 4.0

def test_travel_scoring():
    # 15 travel days/month
    details = calculate_score_details(30, 70, 175, 40, 2, 0.5, 8, 15, 4, 1)
    assert details["travel_score"] == 2.0


# ----------------- BIOMETRICS SCORE (3 scenarios) -----------------
def test_biometrics_healthy_bmi():
    # BMI is ~22.8 (Healthy)
    details = calculate_score_details(30, 70, 175, 40, 2, 0.5, 8, 2, 4, 1)
    assert details["biometrics_score"] == 10.0

def test_biometrics_overweight():
    # Weight 88, Height 175 -> BMI ~28.7
    details = calculate_score_details(30, 88, 175, 40, 2, 0.5, 8, 2, 4, 1)
    assert details["biometrics_score"] == 6.3

def test_biometrics_obese():
    # Weight 100, Height 170 -> BMI ~34.6
    details = calculate_score_details(30, 100, 170, 40, 2, 0.5, 8, 2, 4, 1)
    assert details["biometrics_score"] == 2.7


# ----------------- CATEGORY MAPPING (4 scenarios) -----------------
def test_get_category_elite():
    assert get_category(90) == "Elite Corporate Athlete"

def test_get_category_warrior():
    assert get_category(72) == "Weekend Warrior"

def test_get_category_sedentary():
    assert get_category(52) == "Sedentary Corporate Warrior"

def test_get_category_burnout():
    assert get_category(35) == "Executive Burnout Risk"


# ----------------- FITNESS POTENTIALS (3 scenarios) -----------------
def test_fitness_potential_steps():
    # Baseline checks for steps calculations
    potential = calculate_fitness_potential(
        score=70, gender="Male", age=30, weight=75.0, height=178.0,
        training_days=3, meetings_per_day=3, commute_hours=1.0, work_hours=45
    )
    assert potential["steps_target"] > 0
    # Steps target should be rounded to nearest 500
    assert potential["steps_target"] % 500 == 0

def test_fitness_potential_body_fat():
    pot_male = calculate_fitness_potential(
        score=80, gender="Male", age=30, weight=75.0, height=178.0,
        training_days=4, meetings_per_day=2, commute_hours=0.5, work_hours=40
    )
    pot_female = calculate_fitness_potential(
        score=80, gender="Female", age=30, weight=75.0, height=178.0,
        training_days=4, meetings_per_day=2, commute_hours=0.5, work_hours=40
    )
    # Female bf range should be higher than male range
    assert float(pot_female["body_fat_range"].split("%")[0]) > float(pot_male["body_fat_range"].split("%")[0])


# ----------------- LIMITERS DETECTION (2 scenarios) -----------------
def test_detect_limiters_sleep_deficit():
    details = calculate_score_details(30, 75, 178, 40, 2, 0.5, 5.0, 2, 4, 1)
    limiters = detect_limiters(details, 5.0, 2, 0.5, 40, 2, 4, 1)
    assert len(limiters) > 0
    assert any(lim["name"] == "Sleep Deficit" for lim in limiters)

def test_detect_limiters_empty_for_perfect_health():
    # Perfect score, no limiters
    details = calculate_score_details(30, 75, 178, 35, 1, 0.2, 8.5, 0, 5, 1)
    limiters = detect_limiters(details, 8.5, 1, 0.2, 35, 0, 5, 1)
    # Since sleep >= 7, work <= 45, meetings <= 4, stress <= 6, travel <= 4, training >= 3, commute <= 1,
    # no limiters should fire.
    assert len(limiters) == 0


# ----------------- PROMOTION SIMULATOR (2 scenarios) -----------------
def test_simulate_promotion_score_drop():
    current_metrics = {
        "age": 30, "weight": 75.0, "height": 178.0, "gender": "Male",
        "work_hours": 40.0, "meetings_per_day": 2.0, "commute_hours": 0.5,
        "sleep_hours": 8.0, "travel_days": 1.0, "training_days": 4.0, "stress_level": 2.0
    }
    sim = simulate_promotion("Director / VP", current_metrics)
    assert sim["simulated_score"] < sim["current_score"]

def test_simulate_promotion_ceo_severe_drop():
    current_metrics = {
        "age": 30, "weight": 75.0, "height": 178.0, "gender": "Male",
        "work_hours": 40.0, "meetings_per_day": 2.0, "commute_hours": 0.5,
        "sleep_hours": 8.0, "travel_days": 1.0, "training_days": 4.0, "stress_level": 2.0
    }
    sim_ceo = simulate_promotion("Founder / CEO", current_metrics)
    sim_se = simulate_promotion("Senior Engineer", current_metrics)
    # CEO impact should drop score more than Senior Engineer
    assert sim_ceo["simulated_score"] < sim_se["simulated_score"]
