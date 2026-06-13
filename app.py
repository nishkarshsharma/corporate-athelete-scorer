from altair.utils import deprecation
from asyncio import coroutines
import streamlit as st
import os
from dotenv import load_dotenv
from textwrap import dedent

from config import settings
from src import score_engine
from src import coach_engine
from src.utils import lead_manager

load_dotenv()

# Page Config
st.set_page_config(
    page_title="Corporate Athlete Scorer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load External Styling from stylesheet
css_path = os.path.join("src", "styles", "main.css")
try:
    with open(css_path, "r", encoding="utf-8") as f:
        css_style = f.read()
    st.markdown(f"<style>{css_style}</style>", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Unable to load custom stylesheet: {e}. Falling back to default styling.")

# App Header
st.markdown("""
<div style='text-align: center; margin-bottom: 30px;'>
    <h1 class="hero-title">
        💼 <span class="gradient-text">CORPORATE ATHLETE</span> SCORER
    </h1>
    <p style='color: #94a3b8; font-size: 1.1rem; max-width: 700px; margin: 0 auto;'>
        Measure your physiological resilience. Optimize sleep, meetings, commute, and training to prevent burnout and peak your professional performance.
    </p>
</div>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR INPUTS -----------------
with st.sidebar:
    st.markdown("### 📊 Your Profile Metrics")
    
    with st.expander("👤 Biometrics", expanded=True):
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.slider("Age (years)", 18, 80, 32)
        weight = st.number_input("Weight (kg)", 40.0, 160.0, 78.0, step=0.5)
        height = st.number_input("Height (cm)", 120, 220, 178)
        
    with st.expander("💼 Career & Workload", expanded=True):
        job_role = st.text_input("Job Title / Role", placeholder="e.g., Senior Engineer, Director") # NEW PARAMETER
        user_goal = st.selectbox("Primary Focus Goal", ["Prevent Burnout", "Optimize Energy", "Build Muscle/Lose Fat", "Improve Sleep Resilience"]) # NEW PARAMETER
        work_hours = st.slider("Weekly Work Hours", 20, 100, 48, step=1)
        meetings_per_day = st.slider("Daily Meetings", 0, 15, 5, step=1)
        commute_hours = st.slider("Daily Commute (hrs/day)", 0.0, 6.0, 1.2, step=0.1)
        
    with st.expander("🌱 Wellness & Lifestyle", expanded=True):
        sleep_hours = st.slider("Daily Sleep (hours)", 3.0, 11.0, 6.5, step=0.1)
        travel_days = st.slider("Business Travel Days/Month", 0, 30, 3, step=1)
        training_days = st.slider("Weekly Training Days", 0, 7, 2, step=1)
        stress_level = st.slider("Cognitive Stress (1-10)", 1, 10, 7)

    with st.expander("🔑 Hugging Face API Settings", expanded=False):
        api_key = st.text_input(
            "Hugging Face API Key", 
            type="password", 
            value=os.environ.get(settings.HF_TOKEN_ENV_VAR, ""), 
            help="Provide your Hugging Face API Key to enable custom, generative coaching advice. Falls back to local Rules Engine otherwise."
        )

# ----------------- DATA PREPARATION & DETACHED AUTO-SAVE FLOW -----------------
current_metrics = {
    "age": age,
    "weight": weight,
    "height": height,
    "gender": gender,
    "work_hours": float(work_hours),
    "meetings_per_day": float(meetings_per_day),
    "commute_hours": float(commute_hours),
    "sleep_hours": float(sleep_hours),
    "travel_days": float(travel_days),
    "training_days": float(training_days),
    "stress_level": float(stress_level)
}

# Calculate baseline details
score_details = score_engine.calculate_score_details(**current_metrics)
score = score_details["total_score"]
category = score_engine.get_category(score)
limiters = score_engine.detect_limiters(
    score_details, sleep_hours, meetings_per_day, commute_hours,
    work_hours, travel_days, training_days, stress_level
)
potential = score_engine.calculate_fitness_potential(
    score, gender, age, weight, height, training_days, meetings_per_day, commute_hours, work_hours
)

# Extract top limiter parameters using deterministic engine rules directly
top_limiter_name = limiters[0]["name"] if limiters else "None"
recommended_action_text = limiters[0]["recommendation"] if limiters else "Maintain current wellness trajectory."

# Initialize Session State Variables cleanly
if "current_assessment_id" not in st.session_state:
    st.session_state.current_assessment_id = None
if "coach_report" not in st.session_state:
    st.session_state.coach_report = None
if "last_processed_metrics" not in st.session_state:
    st.session_state.last_processed_metrics = None

# CRITICAL P0 STEP: Handle state mutations to trigger unique assessment entries
# If user changes sliders, calculate a brand-new assessment ID immediately.
if st.session_state.last_processed_metrics != current_metrics:
    st.session_state.last_processed_metrics = current_metrics
    st.session_state.coach_report = None  # Reset report state so it updates against new values
    
    # Pack unified dictionary containing core metrics alongside the extended payload attributes
    save_payload = {
        "score": score,
        "category": category,
        "age": age,
        "gender": gender,
        "work_hours": work_hours,
        "meetings_per_day": meetings_per_day,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level,
        "top_limiter": top_limiter_name,
        "recommended_action": recommended_action_text,
        "user_goal": user_goal,
        "job_role": job_role
    }
    
    # Save base structural assessment row immediately to Google Sheets database log
    # Pass an empty string for the email since PII email capture is handled asynchronously on Tab 4
    st.session_state.current_assessment_id = lead_manager.save_assessment(
        email="", 
        metrics_data=save_payload
    )

# Render Score Ring CSS classes matching your stylesheet perfectly
if score >= 81:
    stroke_color = "#10b981"  # Emerald
    cat_class = "cat-elite"
elif score >= 61:
    stroke_color = "#06b6d4"  # Cyan
    cat_class = "cat-warrior"
elif score >= 41:
    stroke_color = "#f59e0b"  # Amber
    cat_class = "cat-sedentary"
else:
    stroke_color = "#ef4444"  # Red
    cat_class = "cat-burnout"

circumference = 502.65
offset = circumference - (score / 100.0) * circumference

# ----------------- TABS SETUP -----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Analysis", 
    "🎙️ AI Coach", 
    "⚡ Simulator", 
    "💾 Benchmark"
])

# ----------------- TAB 1: SCORE & ANALYSIS -----------------
with tab1:
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown(f"""
            <h3 style="margin: 0 0 10px 0; font-weight: 700; font-size: 1.25rem; color: var(--text-color);">Score Overview</h3> 
            
            <div class="score-container">
                <div class="score-ring">
                    <svg width="200" height="200" viewBox="0 0 200 200">
                        <circle class="score-ring-circle-bg" cx="100" cy="100" r="80" />
                        <circle class="score-ring-circle-fg" cx="100" cy="100" r="80" 
                                stroke="{stroke_color}" 
                                stroke-dasharray="{circumference}" 
                                stroke-dashoffset="{offset}" />
                    </svg>
                    <div class="score-text">
                        <div class="score-num">{score}</div>
                        <div class="score-denom">Athlete Score</div>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin-bottom: 20px;">
                <span class="category-badge {cat_class}">{category}</span>
            </div>
            
            <div class="metrics-summary-block" style="border-top: 1px solid rgba(128,128,128,0.15); padding-top: 15px; margin-top: 10px;">
                <p style="font-size: 0.9rem; margin: 8px 0; color: var(--text-color);">
                    BMI: <strong style="color: var(--text-color);">{score_details['bmi']}</strong> 
                    <span style="opacity: 0.5; font-size: 0.8rem;">(Healthy range: 18.5 - 24.9)</span>
                </p>
                <p style="font-size: 0.9rem; margin: 8px 0; color: var(--text-color);">
                    Training Days: <strong style="color: var(--text-color);">{training_days} / week</strong>
                </p>
                <p style="font-size: 0.9rem; margin: 8px 0; color: var(--text-color);">
                    Sleep Hours: <strong style="color: var(--text-color);">{sleep_hours} / night</strong>
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # PROJECTED FITNESS POTENTIAL CARD
        st.markdown(f"""
            <h3 style="margin-top: 0; margin-bottom: 15px; font-weight: 700; font-size: 1.15rem; color: var(--text-color);">🎯 Projected Fitness Potential</h3>
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <div>
                    <div class="metric-lbl">Realistic Body Fat Potential</div>
                    <div style="font-weight: 700; font-size: 1.2rem; color: var(--text-color); margin-top: 2px;">{potential.get('body_fat_range', 'N/A')}</div>
                </div>
                <div>
                    <div class="metric-lbl">Daily Step Target</div>
                    <div style="font-weight: 700; font-size: 1.2rem; color: var(--text-color); margin-top: 2px;">{potential.get('steps_target', 0):,} steps</div>
                </div>
                <div>
                    <div class="metric-lbl">Target Gym Sessions</div>
                    <div style="font-weight: 700; font-size: 1.2rem; color: var(--text-color); margin-top: 2px;">{potential.get('gym_sessions_target', 'N/A')} / week</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_right:
        # CATEGORY BREAKDOWN CARD
        st.markdown(f"""
            <h4 style="margin-top: 0; font-weight: 700; color: var(--text-color);">🧭 Category Breakdown</h4>
            <div style="display: flex; justify-content: space-between; margin-top: 15px; flex-wrap: wrap; gap: 10px;">
                <div style="text-align: center; flex: 1; min-width: 80px;">
                    <div class="metric-lbl" style="font-size:0.8rem; color:#94a3b8;">Sleep</div>
                    <div class="metric-val" style="font-size: 1.5rem; font-weight:700; color: #10b981;">{score_details['sleep_score']}<span style="font-size: 0.8rem; opacity: 0.6;">/25</span></div>
                </div>
                <div style="text-align: center; flex: 1; min-width: 80px;">
                    <div class="metric-lbl" style="font-size:0.8rem; color:#94a3b8;">Workload</div>
                    <div class="metric-val" style="font-size: 1.5rem; font-weight:700; color: #3b82f6;">{score_details['work_meetings_score']}<span style="font-size: 0.8rem; opacity: 0.6;">/20</span></div>
                </div>
                <div style="text-align: center; flex: 1; min-width: 80px;">
                    <div class="metric-lbl" style="font-size:0.8rem; color:#94a3b8;">Activity</div>
                    <div class="metric-val" style="font-size: 1.5rem; font-weight:700; color: #ec4899;">{score_details['physical_activity_score']}<span style="font-size: 0.8rem; opacity: 0.6;">/25</span></div>
                </div>
                <div style="text-align: center; flex: 1; min-width: 80px;">
                    <div class="metric-lbl" style="font-size:0.8rem; color:#94a3b8;">Stress</div>
                    <div class="metric-val" style="font-size: 1.5rem; font-weight:700; color: #f59e0b;">{score_details['stress_travel_score']}<span style="font-size: 0.8rem; opacity: 0.6;">/20</span></div>
                </div>
                <div style="text-align: center; flex: 1; min-width: 80px;">
                    <div class="metric-lbl" style="font-size:0.8rem; color:#94a3b8;">Biometrics</div>
                    <div class="metric-val" style="font-size: 1.5rem; font-weight:700; color: #8b5cf6;">{score_details['biometrics_score']}<span style="font-size: 0.8rem; opacity: 0.6;">/10</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # KEY LIMITERS CARD
        if not limiters:
            st.success("Outstanding! You have no major energy drains or score limiters.")
        else:
            limiters_combined_html = "<h4 style='color: var(--text-color); margin-bottom: 12px;'>⚠️ Key Limiters & Energy Drains</h4>"
            
            for lim in limiters:
                border_color = "#ef4444" if lim["score_impact"] > 6 else "#f59e0b"
                limiters_combined_html += (
                    f'<div class="limiter-box" style="border-left: 4px solid {border_color}; background: rgba(128, 128, 128, 0.04); padding: 12px; margin-bottom: 10px; border-radius: 0 8px 8px 0;">'
                    f'<div class="limiter-title" style="font-weight: 700; font-size: 1rem; margin-bottom: 4px; color: var(--text-color);">{lim["name"]} <span style="font-size: 0.9rem; font-weight: 500; opacity: 0.85;">(Drains -{round(lim["score_impact"], 1)} pts)</span></div>'
                    f'<div style="font-size: 0.85rem; margin-bottom: 6px; color: var(--text-color); opacity: 0.7;">Metric value: <strong>{lim["stat"]}</strong></div>'
                    f'<div class="limiter-rec" style="font-size: 0.9rem; color: var(--text-color); line-height: 1.4;">{lim["recommendation"]}</div>'
                    f'</div>'
                )
            
            st.markdown(limiters_combined_html, unsafe_allow_html=True)

# ----------------- TAB 2: AI PERFORMANCE COACH -----------------
with tab2:
    with st.container():
        st.markdown("### 🎙️ Personalized AI Coaching Report")
        st.markdown(
            "Generate a bespoke coaching assessment powered by **AI** "
            "designed to optimize your physiology around your busy corporate lifestyle."
        )
        
        has_api_key = bool(api_key or os.environ.get(settings.HF_TOKEN_ENV_VAR))
        if not has_api_key:
            st.info("💡 You are viewing the rules-based fallback coaching plan. Enter a Hugging Face API Key in the sidebar for customized, AI-driven guidance.")
        else:
            st.success("🤖 AI Performance Coach is connected. Click below to analyze.")

        if st.button("Generate Coaching Protocol", type="primary"):
            with st.spinner("Analyzing metrics and formulating executive advice..."):
                st.session_state.coach_report = coach_engine.get_coaching_report(
                    age=age,
                    weight=weight,
                    height=height,
                    work_hours=work_hours,
                    meetings_per_day=meetings_per_day,
                    commute_hours=commute_hours,
                    sleep_hours=sleep_hours,
                    travel_days=travel_days,
                    training_days=training_days,
                    stress_level=stress_level,
                    gender=gender,
                    api_key=api_key
                )
                
                # UPDATE TRANSACTION: Write the generated report backend string onto the active row tracker
                if st.session_state.coach_report and st.session_state.current_assessment_id:
                    lead_manager.update_ai_response(
                        assessment_id=st.session_state.current_assessment_id,
                        ai_response_text=st.session_state.coach_report["content"]
                    )

        # Render report from session state persistent container
        if st.session_state.coach_report:
            report = st.session_state.coach_report
            source_badge = (
                '<span class="category-badge cat-elite" style="margin-bottom: 20px;">🤖 AI Flash Coach</span>'
                if report["is_ai"] else 
                '<span class="category-badge cat-sedentary" style="margin-bottom: 20px;">🧭 Rule-Based Coach Fallback</span>'
            )
            st.markdown(source_badge, unsafe_allow_html=True)
            st.markdown(f"""
                <div class="coach-report">
                    {report["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

# ----------------- TAB 3: PROMOTION SIMULATOR -----------------
with tab3:
    with st.container():
        st.markdown("### ⚡ Career Promotion Impact Simulator")
        st.markdown(
            "How will climbing the corporate ladder affect your physical baseline? "
            "Select a promotion tier to simulate how increased workload, meetings, and travel will drag down your score."
        )
        
        promo_tier = st.selectbox(
            "Select Target Promotion Level",
            list(settings.PROMOTION_IMPACTS.keys())
        )
        
        sim_results = score_engine.simulate_promotion(promo_tier, current_metrics)
        delta_score = sim_results["simulated_score"] - sim_results["current_score"]
        
        col_cur, col_sim = st.columns(2)
        
        with col_cur:
            st.markdown(f"""
            <div class="promo-col good">
                <h4 style="margin: 0; opacity: 0.85; font-size: 1.05rem; font-weight: 600;">Current Balance</h4>
                <div class="metric-val" style="font-size: 3.2rem; font-weight: 800; color: #10b981; line-height: 1.1;">{sim_results['current_score']}</div>
                <div class="category-badge cat-warrior" style="margin: 4px 0 0 0; display: inline-block;">{sim_results['current_category']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_sim:
            st.markdown(f"""
            <div class="promo-col bad">
                <h4 style="margin: 0; opacity: 0.85; font-size: 1.05rem; font-weight: 600;">Simulated {promo_tier}</h4>
                <div class="metric-val" style="font-size: 3.2rem; font-weight: 800; color: #ef4444; line-height: 1.1;">{sim_results['simulated_score']}</div>
                <div class="category-badge cat-burnout" style="margin: 4px 0 0 0; display: inline-block;">{sim_results['simulated_category']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 🚨 The Career Impact Breakdown")
        deltas = sim_results["metric_deltas"]
        
        warning_text = f"""
        <div class="viral-warning-card">
            <h4 class="danger-text" style="margin-top: 0; margin-bottom: 8px;">VIRAL PREDICTION DETECTED</h4>
            <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 0;">
                "Your promotion to <strong>{promo_tier}</strong> is predicted to increase your workload by <strong>+{int(deltas['work_hours'])} hours/week</strong>, 
                add <strong>+{int(deltas['meetings_per_day'])} meetings/day</strong>, increase travel by <strong>+{int(deltas['travel_days'])} days/month</strong>, 
                and cut sleep by <strong>-{int(abs(deltas['sleep_hours'])*60)} minutes/day</strong>.
                As a result, your Corporate Athlete Score will drop by <strong style="text-decoration: underline;">{abs(delta_score)} points</strong> (from {sim_results['current_score']} to {sim_results['simulated_score']}). 
                Your predicted body fat is projected to increase from <strong>{sim_results['current_potential']['body_fat_range']}</strong> to <strong>{sim_results['simulated_potential']['body_fat_range']}</strong> due to metabolic stress and training sacrifice."
            </p>
        </div>
        """
        st.markdown(warning_text, unsafe_allow_html=True)
        
        st.markdown("### 📊 Metrics Shift Comparison")
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            st.markdown(f"""
            <div class="premium-card">
                <h4 style="margin-top: 0;">Workload & Travel Shifts</h4>
                <div class="comp-metric">
                    <span style="opacity: 0.85;">Weekly Work Hours</span>
                    <span>{current_metrics['work_hours']} hrs ➔ <strong>{sim_results['simulated_metrics']['work_hours']} hrs</strong> <span style="color: #ef4444;">(+{int(deltas['work_hours'])})</span></span>
                </div>
                <div class="comp-metric">
                    <span style="opacity: 0.85;">Daily Meetings</span>
                    <span>{current_metrics['meetings_per_day']} ➔ <strong>{sim_results['simulated_metrics']['meetings_per_day']}</strong> <span style="color: #ef4444;">(+{int(deltas['meetings_per_day'])})</span></span>
                </div>
                <div class="comp-metric">
                    <span style="opacity: 0.85;">Travel Days/Month</span>
                    <span>{current_metrics['travel_days']} ➔ <strong>{sim_results['simulated_metrics']['travel_days']}</strong> <span style="color: #ef4444;">(+{int(deltas['travel_days'])})</span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with comp_col2:
            st.markdown(f"""
            <div class="premium-card">
                <h4 style="margin-top: 0;">Health & Wellness Sacrifices</h4>
                <div class="comp-metric">
                    <span style="opacity: 0.85;">Daily Sleep Hours</span>
                    <span>{current_metrics['sleep_hours']} hrs ➔ <strong>{sim_results['simulated_metrics']['sleep_hours']} hrs</strong> <span style="color: #ef4444;">({deltas['sleep_hours']} hrs)</span></span>
                </div>
                <div class="comp-metric">
                    <span style="opacity: 0.85;">Training Days/Week</span>
                    <span>{current_metrics['training_days']} days ➔ <strong>{sim_results['simulated_metrics']['training_days']} days</strong> <span style="color: #ef4444;">({deltas['training_days']} days)</span></span>
                </div>
                <div class="comp-metric">
                    <span style="opacity: 0.85;">Cognitive Stress (1-10)</span>
                    <span>{current_metrics['stress_level']} ➔ <strong>{sim_results['simulated_metrics']['stress_level']}</strong> <span style="color: #ef4444;">(+{int(deltas['stress_level'])})</span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ----------------- TAB 4: SAVE & BENCHMARK -----------------
with tab4:
    with st.container():
        st.markdown("### 💾 Secure Your Performance Benchmarking")
        st.markdown(
            "Capture your score in our database to compare yourself with the anonymous aggregate corporate metrics. "
            "We will save your email into marketing and correlate your metrics anonymously via security hashes."
        )
        
        percentile = lead_manager.calculate_score_percentile(score)
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.markdown(f"""
            <div style="text-align: center; background: rgba(128,128,128,0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(128,128,128,0.15);">
                <div class="metric-lbl">Your Current Score</div>
                <div class="metric-val" style="color: {stroke_color}; font-size: 2.5rem; font-weight: 800;">{score}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_stat2:
            st.markdown(f"""
            <div style="text-align: center; background: rgba(128,128,128,0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(128,128,128,0.15);">
                <div class="metric-lbl">Corporate Benchmarking Average</div>
                <div class="metric-val" style="color: #888888; font-size: 2.5rem; font-weight: 800;">{settings.BENCHMARK_AVG_SCORE}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_stat3:
            st.markdown(f"""
            <div style="text-align: center; background: rgba(128,128,128,0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(128,128,128,0.15);">
                <div class="metric-lbl">Your Corporate Percentile</div>
                <div class="metric-val" style="color: #06b6d4; font-size: 2.5rem; font-weight: 800;">Top {100 - percentile}%</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("lead_form", clear_on_submit=False):
            email = st.text_input("Enter your Professional Email Address", placeholder="exec@company.com")
            submit_btn = st.form_submit_button("Lock in my score & benchmark it", type="primary")
            consent = st.checkbox(
                "I agree to the Privacy Policy and allow Corporate Athlete Scorer to safely process "
                "and anonymize my metrics for corporate benchmarking purposes."
            )
            if submit_btn:
                if not consent:
                    st.error("You must agree to the data processing terms to calculate your benchmark.")
                elif not email or "@" not in email or "." not in email:
                    st.error("❌ Please enter a valid email address.")
                else:
                    st.success("Compliance verified! Saving PII variables safely...")
                    
                    # Store plain text email to marketing sheet safely
                    lead_manager.save_marketing_lead(email)
                    
                    # Update active assessment row matching active hash values securely
                    email_hash = lead_manager._hash_email(email)
                    try:
                        # Find matching index cell and update hash securely
                        cell = lead_manager.metrics_sheet.find(st.session_state.current_assessment_id, in_column=11)
                        if cell:
                            lead_manager.metrics_sheet.update_cell(cell.row, 9, email_hash)
                        
                        st.success(f"🎉 Your score of **{score}** has been benchmarked! We've saved your result successfully.")
                        
                        total_participants = len(lead_manager.get_leads_snapshot(1000))
                        st.metric(label="Global Athletes Benchmarked", value=f"{total_participants} professionals")
                    except Exception as e:
                        st.error(f"❌ Cloud Write Failure: Failed to link anonymized email parameter: {e}")