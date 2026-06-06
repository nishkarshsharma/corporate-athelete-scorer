I will update the `README.md` to perfectly match your implementation.

I noticed a couple of mathematical notations in your draft like `$\text{Score} \in [0, 100]$`. To keep your markdown pristine, clean, and completely native to GitHub's markdown renderer (which can sometimes choke on inline math expressions in standard prose blocks), I've simplified them into clean, bolded inline text.

Here is your fully updated, professional `README.md` ready to be committed to your repository:

```markdown
# 💼 Corporate Athlete Scorer

A premium, interactive Streamlit application designed for elite professionals to evaluate their lifestyle, stress, sleep, and activity metrics. By analyzing corporate-induced constraints, the app calculates a personalized **Corporate Athlete Score** (ranging from **0 to 100**) and provides actionable, high-performance recovery strategies.

The application features a rule-based scoring engine, an AI-powered executive coaching report via Google Gemini, a viral *Promotion Impact Simulator*, and a secure lead capture benchmarking system.

---

## 🚀 Features

* **📊 Detailed Scoring Breakdown:** Analyzes critical variables including sleep duration, active work hours, meeting densities, daily commute times, physical activity levels, travel loads, and BMI to construct an itemized high-performance report card.
* **📈 Projected Fitness Potential:** Estimates realistic body fat percentages, optimized daily step count targets, and weekly training volume adjustments tailored specifically around heavy corporate schedules.
* **⚠️ Key Limiters Detection:** Automatically identifies and highlights the primary biological and environmental bottlenecks draining your daily energy.
* **🎙️ Gemini Flash Coaching:** Integrates with the Google GenAI SDK (`gemini-2.5-flash`) to generate highly customized, realistic 1-week micro-habit execution schedules. *Falls back gracefully to a robust rule-based engine if an API key is absent.*
* **⚡ Promotion Impact Simulator:** A predictive simulator showing how future career advancements (e.g., Senior Engineer → Engineering Manager → Director/VP → Founder/CEO) will structurally shift your health metrics and impact your baseline score.
* **🔒 Secure Lead Capture & Benchmarking:** Appends lead data safely to Google Sheets and local backups (`data/leads.csv`), dynamically calculating corporate percentile ratings against other professionals.

---

## 🔒 Data Privacy & Lead Integrity

To maintain compliance and protect user anonymity while offering comparative benchmarks, the data pipeline cleanly isolates internal storage from public-facing analytics:
* **Primary Database / Google Sheets:** Captures raw, pristine lead communication strings (such as plain-text emails) for CRM tracking and standard administrative lookups.
* **Benchmarking Engine:** For downstream processing, public leaderboards, or anonymous comparative distributions, the pipeline creates isolated, non-mutating deep copies of user telemetry and uses cryptographic hashing for public unique identifiers, avoiding side effects or references bleeding into the persistent sheet layer.

---

## 🛠️ Tech Stack

* **Frontend UI:** Streamlit
* **AI Core Engine:** Google GenAI SDK (`gemini-2.5-flash`)
* **Data Processing:** Python 3.11+ & Pandas
* **Testing Framework:** Pytest

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/nishkarshsharma/corporate-athelete-scorer.git](https://github.com/nishkarshsharma/corporate-athelete-scorer.git)
cd corporate-athelete-scorer

```

### 2. Install Dependencies

Ensure you have Python 3.11+ installed, then run:

```bash
pip install -r requirements.txt

```

Create a `.env` file in the root directory to automatically load your Gemini API configurations:

```env
GEMINI_API_KEY=your_api_key_here

```

*Note: You can also enter your API key directly into the application sidebar at runtime.*

### 4. Run the Application

Launch the Streamlit server locally:

```bash
streamlit run app.py

```

---

## 🧪 Running Tests

The repository includes comprehensive automated test suites to validate scoring logic, health limiters, and data serialization flows. Run them via `pytest`:

```bash
pytest
```