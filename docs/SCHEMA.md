# NutriEase — Database Schema (SQLite)

The database lives at `data/nutriease.sqlite`. It is created automatically on first run.

## users
| Column         | Type     | Notes                          |
|----------------|----------|--------------------------------|
| id             | INTEGER  | PK                             |
| email          | TEXT     | UNIQUE, indexed                |
| password_hash  | TEXT     | werkzeug PBKDF2 hash           |
| full_name      | TEXT     |                                |
| is_admin       | BOOLEAN  | default 0                      |
| created_at     | DATETIME |                                |
| last_login     | DATETIME |                                |

## profiles
One-to-one with `users`. Stores age, gender, height_cm, weight_kg, activity_level, goal, diet_preference, allergies, deficiencies, medical_conditions.

## diet_plans
Per-user generated plans (`plan_json` is the serialised plan).

## deficiency_reports
Symptom → likely deficiency reports.

## conversations / messages
Chat history. `conversations.state` is `onboarding` or `free`; `state_data` stores the in-progress onboarding answers as JSON.

## weight_logs
Weight entries for progress tracking.

## reminders
Meal / workout / water reminders with time-of-day.

## password_reset_otps
Six-digit OTP records with expiry timestamp for the forgot-password flow.
