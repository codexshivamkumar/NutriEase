"""NutriEase conversational engine.

Combines:
  * a doctor-style onboarding flow that collects profile data
  * Mifflin-St Jeor BMR + activity multiplier for calorie targets
  * BMI calculation and category
  * a TF-IDF retrieval model trained on 100,000+ Q&A pairs
  * lightweight spelling correction with difflib
"""
import os, re, json, joblib, difflib

HERE = os.path.dirname(__file__)
MODEL_PATH = os.path.join(HERE, "data", "chatbot_model.joblib")

_model = None
_vocab = None


def _load_model():
    global _model, _vocab
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            from train_model import main as train
            train()
        _model = joblib.load(MODEL_PATH)
        _vocab = list(_model["vectorizer"].vocabulary_.keys())
    return _model


# ------------- Spelling correction -------------

_WORD = re.compile(r"[a-zA-Z']+")

def correct_spelling(text: str) -> str:
    """Best-effort token-level correction using the model vocabulary."""
    _load_model()
    out = []
    for tok in _WORD.findall(text):
        low = tok.lower()
        if low in _vocab or len(low) <= 2:
            out.append(tok)
            continue
        match = difflib.get_close_matches(low, _vocab, n=1, cutoff=0.86)
        out.append(match[0] if match else tok)
    return " ".join(out) if out else text


# ------------- Health math -------------

def bmi(weight_kg: float, height_cm: float) -> float:
    h = height_cm / 100.0
    return round(weight_kg / (h * h), 1)


def bmi_category(value: float) -> str:
    if value < 18.5: return "Underweight"
    if value < 25:   return "Normal"
    if value < 30:   return "Overweight"
    return "Obese"


def bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> int:
    # Mifflin-St Jeor
    s = 5 if (gender or "").lower().startswith("m") else -161
    return int(round(10 * weight_kg + 6.25 * height_cm - 5 * age + s))


ACTIVITY = {
    "sedentary": 1.2, "light": 1.375, "moderate": 1.55,
    "active": 1.725, "very_active": 1.9,
}

GOAL_ADJUST = {"lose": -500, "maintain": 0, "gain": 400, "muscle": 300}


def daily_calories(profile: dict) -> int:
    b = bmr(profile["weight_kg"], profile["height_cm"], profile["age"], profile["gender"])
    tdee = b * ACTIVITY.get(profile.get("activity_level", "moderate"), 1.55)
    return int(round(tdee + GOAL_ADJUST.get(profile.get("goal", "maintain"), 0)))


# ------------- Doctor-style onboarding flow -------------

ONBOARDING_STEPS = [
    ("name",            "Hello! I'm your NutriEase coach. May I have your name to get started?"),
    ("age",             "Nice to meet you, {name}. How old are you (in years)?"),
    ("gender",          "Thank you. What is your gender? (male / female / other)"),
    ("height_cm",       "Got it. What's your height in centimetres?"),
    ("weight_kg",       "And your current weight in kilograms?"),
    ("goal",            "What's your main goal — lose, maintain, gain, or muscle?"),
    ("activity_level",  "How active are you day-to-day? (sedentary / light / moderate / active / very_active)"),
    ("diet_preference", "Any dietary preference? (non-vegetarian / vegetarian / vegan)"),
    ("diet_region",     "Would you prefer an Indian or Global diet chart?"),
    ("budget",          "What is your weekly grocery budget? (Low / Medium / High)"),
    ("medical_conditions",
                        "Last one — any medical conditions or allergies I should consider? (type 'none' if not)"),
]


def _parse(field: str, value: str):
    v = value.strip()
    if field in ("age",):
        m = re.search(r"\d+", v); return int(m.group()) if m else None
    if field in ("height_cm", "weight_kg"):
        m = re.search(r"\d+(\.\d+)?", v); return float(m.group()) if m else None
    if field == "gender":
        v = v.lower()
        for k in ("male", "female", "other"):
            if v.startswith(k[0]): return k
        return None
    if field == "goal":
        v = v.lower()
        for k in ("lose", "maintain", "gain", "muscle"):
            if k in v: return k
        return None
    if field == "activity_level":
        v = v.lower().replace(" ", "_")
        for k in ACTIVITY:
            if k in v: return k
        return None
    if field == "diet_preference":
        v = v.lower()
        if "omnivore" in v: return "non-vegetarian"
        for k in ("vegan", "vegetarian", "non-vegetarian", "non veg", "non-veg"):
            if k in v: return "non-vegetarian" if k in ["non veg", "non-veg", "omnivore"] else k
        return "non-vegetarian"
    if field == "diet_region":
        v = v.lower()
        if "indian" in v: return "indian"
        return "global"
    if field == "budget":
        v = v.lower()
        if "low" in v: return "low"
        if "high" in v: return "high"
        return "medium"
    if field == "name":
        return v.title()[:60] if v else None
    if field == "medical_conditions":
        return "" if v.lower() in ("none", "no", "n/a") else v[:300]
    return v


def onboarding_next(state: dict, user_text: str | None):
    """Return (assistant_reply, next_state, finished_summary_or_none)."""
    data = state.setdefault("data", {})
    idx = state.get("idx", 0)

    if user_text is not None and idx > 0:
        prev_field, _ = ONBOARDING_STEPS[idx - 1]
        parsed = _parse(prev_field, user_text)
        if parsed is None and prev_field not in ("medical_conditions",):
            return (f"Sorry, I didn't catch that. {ONBOARDING_STEPS[idx - 1][1].format(**data)}",
                    state, None)
        data[prev_field] = parsed

    if idx >= len(ONBOARDING_STEPS):
        # Final summary
        b = bmi(data["weight_kg"], data["height_cm"])
        cat = bmi_category(b)
        cal = daily_calories(data)
        
        from diet_planner import generate_one_day_chart_str
        chart_str = generate_one_day_chart_str(data)

        summary = (
            f"Thanks {data.get('name','')}, here is what I found:\n\n"
            f"• BMI: {b} ({cat})\n"
            f"• Estimated daily calories: ~{cal} kcal/day for your goal '{data.get('goal')}'\n"
            f"• Suggested split: ~{int(cal*0.30/4)} g protein, "
            f"~{int(cal*0.45/4)} g carbs, ~{int(cal*0.25/9)} g fats.\n\n"
            "Here is a sample 1-day diet chart based on your preferences:\n\n"
            f"{chart_str}\n\n"
            "I've saved this to your profile. You can now ask me anything — "
            "meal ideas, workouts, supplements, or open the dashboard to generate a full 7-day diet plan."
        )
        state["idx"] = idx
        state["data"] = data
        return summary, state, data

    field, prompt = ONBOARDING_STEPS[idx]
    state["idx"] = idx + 1
    state["data"] = data
    return prompt.format(**data), state, None


# ------------- Free chat (retrieval + personalisation) -------------

def free_answer(question: str, profile: dict | None = None) -> str:
    m = _load_model()
    corrected = correct_spelling(question)
    vec = m["vectorizer"].transform([corrected])
    dists, idxs = m["nn"].kneighbors(vec, n_neighbors=1)
    best = m["answers"][idxs[0][0]]
    confidence = 1 - dists[0][0]

    prefix = ""
    if profile and (profile.get("goal") or profile.get("diet_preference")):
        bits = []
        if profile.get("goal"): bits.append(f"goal: {profile['goal']}")
        if profile.get("diet_preference"): bits.append(f"diet: {profile['diet_preference']}")
        prefix = f"(personalised for your {', '.join(bits)})\n\n"

    if confidence < 0.12:
        return (prefix + "I'm not sure I followed that. Could you rephrase?\n\n"
                "• I can help with diet plans\n"
                "• BMI & Calories calculations\n"
                "• Workouts & Supplements\n"
                "• Deficiencies and goal-based nutrition.")
                
    # Format into 2 lines + bullet points
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', best.strip()) if s.strip()]
    if len(sentences) <= 2:
        return prefix + best
        
    out_text = " ".join(sentences[:2]) + "\n\n"
    for s in sentences[2:]:
        out_text += f"• {s}\n"
        
    return prefix + out_text.strip()


# ------------- Public entry point -------------

def reply(conversation, user_text: str, profile: dict | None = None):
    """Single entry point used by the Flask route.

    Mutates `conversation.state` / `conversation.state_data` for onboarding flows.
    Returns the assistant's text reply and an optional finished-summary dict.
    """
    state = json.loads(conversation.state_data or "{}")

    if conversation.state == "onboarding":
        text, state, finished = onboarding_next(state, user_text)
        conversation.state_data = json.dumps(state)
        if finished is not None:
            conversation.state = "free"
        return text, finished

    return free_answer(user_text, profile=profile), None


def start_onboarding(conversation):
    state = {"idx": 0, "data": {}}
    conversation.state = "onboarding"
    conversation.state_data = json.dumps(state)
    text, state, _ = onboarding_next(state, None)
    conversation.state_data = json.dumps(state)
    return text
