# 💼 Corporate Athlete Scorer

A premium, interactive Streamlit application that evaluates a corporate professional's lifestyle, stress, sleep, and activity metrics to calculate a **Corporate Athlete Score** (0-100). The app features a rule-based scoring engine, a GenAI coaching report (via Gemini Flash), a viral Promotion Impact Simulator, and a lead capture benchmarking system.

## 🚀 Features

- **Detailed Scoring Breakdown**: Checks sleep, work hours, meetings, commute time, physical activity, travel load, and BMI to construct a detailed report card.
- **Projected Fitness Potential**: Estimates realistic body fat, daily step counts, and weekly training targets based on your corporate constraints.
- **Key Limiters Detection**: Identifies the primary bottlenecks draining your daily energy.
- **🎙️ Gemini Flash Coaching**: Integrates with Google Gemini Flash to generate realistic, personalized 1-week micro-habit schedules. Falls back gracefully to rule-based advice if no API key is specified.
- **⚡ Promotion Impact Simulator**: Simulates how job promotions (e.g., Senior Engineer, Engineering Manager, Director/VP, Founder/CEO) will impact your health metrics and score.
- **💾 Lead Capture & Benchmarking**: Saves benchmarking data to `data/leads.csv` and presents corporate percentile ratings.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Core**: Google GenAI SDK (`gemini-2.5-flash`)
- **Backend Core**: Python 3.11+ & Pandas
- **Testing**: Pytest

---

## 💻 Quick Start

### 1. Clone the repo and navigate inside:
```bash
cd "Corporate Athlete Scorer"
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Gemini API Key:
Create a `.env` file in the root directory:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```
*(Or input it directly into the application sidebar).*

### 4. Run the Streamlit app:
```bash
streamlit run app.py
```

### 5. Run Automated Tests:
```bash
pytest tests/
```
