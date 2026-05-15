# NutriEase

NutriEase is a Flask application for nutrition guidance, meal planning, and a retrieval-based chatbot.

Quick start (Windows, PowerShell):

```powershell
# Create and activate venv (if not already created)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run the app
python app.py
```

Open http://127.0.0.1:5000 in your browser.

Notes for repository best practices
- Large model files under `data/` are ignored by default. To track them, enable Git LFS and update `.gitignore` appropriately.

To initialize a professional GitHub repo locally and push (example):

```bash
# install gh (GitHub CLI) and git-lfs if you plan to push large files
git init
git lfs install
git add .
git commit -m "Initial commit: NutriEase"
# create remote repo (public or private)
gh repo create <USERNAME>/<REPO_NAME> --public --source=. --remote=origin --push

# or manually add remote and push
git remote add origin https://github.com/<USERNAME>/<REPO_NAME>.git
git branch -M main
git push -u origin main
```

Security
- Do not commit secrets or environment credentials. Use environment variables or a secrets store.

License
- MIT by default (see LICENSE file).
# NutriEase — Fitness & Nutrition Recommendation Chatbot

A self-hosted, conversational fitness & nutrition coach built in Python by **Shivam Kumar**.

NutriEase behaves like a friendly virtual dietitian: it asks the right questions, computes your BMI and daily calories, and produces a personalised diet plan and workout guidance you can download as a PDF.

> Developer: **Shivam Kumar** · ✉ codexshivam@gmail.com
> © 2026 Shivam Kumar. All rights reserved.

---

## Features

- **Doctor-style chatbot** that asks for name, age, gender, height, weight, goal, activity level, dietary preference and health conditions.
- **BMI** and **Mifflin-St Jeor** based daily calorie estimates with macro splits.
- **7-day diet plans** (omnivore / vegetarian / vegan) with macros and supplements.
- **Workout guidance** for beginner, intermediate and advanced levels.
- **Deficiency analyzer** mapping symptoms to likely vitamin / mineral gaps.
- **PDF export** of any diet plan.
- **Email + password authentication**, secure password hashing, **forgot-password OTP** flow.
- **Admin panel** to monitor users and chatbot activity.
- **Progress tracking** (weight log over time) and **diet history**.
- **Reminders** for meals, workouts and water.
- **NLP preprocessing** with token-level spelling correction.
- **Trained on 100,000+ nutrition / fitness Q&A pairs** using TF-IDF retrieval.
- **REST API** (`/api/chat`, `/api/bmi`).
- Premium dark grey + black theme with green accents and responsive layout.
- SQLite database — zero external dependencies.

---

## Tech stack

- Python 3.10+
- Flask, Flask-Login, Flask-SQLAlchemy
- SQLite (via SQLAlchemy)
- scikit-learn (TF-IDF + NearestNeighbors retrieval)
- ReportLab (PDF export)

---

## Run it from VS Code

1. **Install Python 3.10+** and the **Python extension** for VS Code.
2. **Open the project folder** in VS Code (`File → Open Folder…`).
3. **Open a terminal** (`Terminal → New Terminal`).
4. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```
5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
6. **Generate the dataset and train the chatbot model** (one-time, ~1 min):
   ```bash
   python generate_dataset.py
   python train_model.py
   ```
7. **Run the app**:
   ```bash
   python app.py
   ```
8. Open [http://localhost:5000](http://localhost:5000) in your browser.

### Default admin credentials (auto-created on first run)

- **Email:** `admin@nutriease.local`
- **Password:** `admin1234`

Override via environment variables `NUTRIEASE_ADMIN_EMAIL` / `NUTRIEASE_ADMIN_PASSWORD`. Change them after first sign-in.

---

## Project layout

```
nutriease/
├── app.py                  # Flask routes (auth, chat, dashboard, admin, API)
├── chatbot.py              # Conversational engine, BMI/calorie math, retrieval
├── diet_planner.py         # 7-day diet plan generator
├── deficiency.py           # Symptom → nutrient analyzer
├── pdf_export.py           # ReportLab PDF generator
├── models.py               # SQLAlchemy models (users, profile, plans, …)
├── generate_dataset.py     # Generates 100,000+ Q&A pairs
├── train_model.py          # Trains TF-IDF + NearestNeighbors model
├── requirements.txt
├── data/                   # SQLite DB + dataset + trained model
├── docs/                   # ERD, schema, dataset notes
├── static/style.css        # Dark theme
└── templates/              # Jinja2 templates
```

---

## REST API examples

```bash
curl -X POST http://localhost:5000/api/bmi \
     -H "Content-Type: application/json" \
     -d '{"weight_kg": 72, "height_cm": 178}'

curl -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "best foods for iron deficiency"}'
```

---

## Disclaimer

NutriEase provides educational nutrition guidance and is **not a substitute for medical advice**. Always consult a qualified clinician for medical concerns.
