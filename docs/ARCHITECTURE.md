# NutriEase — Architecture

## Stack
- **Web framework:** Flask 3 + Jinja2 templates (server-rendered HTML)
- **ORM / DB:** SQLAlchemy + SQLite (single file, zero-config)
- **Auth:** Flask-Login + Werkzeug PBKDF2 password hashing
- **PDF:** ReportLab
- **Chatbot ML:** scikit-learn `TfidfVectorizer` + `NearestNeighbors` (cosine), trained on 10,000 generated Q&A pairs

## Request flow

```
Browser ──HTTP──▶ Flask (app.py)
                    │
                    ├─▶ Flask-Login (session cookie)
                    ├─▶ SQLAlchemy ──▶ data/nutriease.sqlite
                    ├─▶ chatbot.py  ──▶ data/chatbot_model.joblib
                    ├─▶ diet_planner.py (pure Python rules)
                    ├─▶ deficiency.py   (pure Python rules)
                    └─▶ pdf_export.py   (ReportLab → bytes)
```

## Chatbot training pipeline

```
generate_dataset.py
    │
    ▼  10,000 (q, a) pairs
data/qa_dataset.jsonl
    │
    ▼  TF-IDF vectorisation + Nearest Neighbour fit
train_model.py
    │
    ▼
data/chatbot_model.joblib   ◀── loaded by chatbot.py at first request
```

## Why SQLite
- Zero-setup, single file, perfect for self-hosted personal use.
- Identical SQL surface to upgrade to MySQL/Postgres later (just change `SQLALCHEMY_DATABASE_URI`).
