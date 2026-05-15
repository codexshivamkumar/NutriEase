"""Symptom -> likely-deficiency analyzer (rule based, with food-first remedies)."""
from generate_dataset import NUTRIENTS

def analyze(symptoms_text: str) -> dict:
    text = symptoms_text.lower()
    scores = {}
    for nutrient, info in NUTRIENTS.items():
        score = 0
        matched = []
        for sym in info["symptoms"]:
            if sym in text:
                score += 1
                matched.append(sym)
        if score:
            scores[nutrient] = (score, matched, info)

    ranked = sorted(scores.items(), key=lambda x: -x[1][0])[:5]
    findings = []
    for nutrient, (score, matched, info) in ranked:
        findings.append({
            "nutrient": nutrient,
            "confidence": min(100, score * 35),
            "matched_symptoms": matched,
            "foods": info["foods"],
            "rda": info["rda"],
            "tip": info["tip"],
        })
    if not findings:
        findings.append({
            "nutrient": "general",
            "confidence": 0,
            "matched_symptoms": [],
            "foods": ["leafy greens", "lentils", "eggs", "fish", "fruits", "nuts and seeds"],
            "rda": "Eat a varied whole-food diet first.",
            "tip": "If symptoms persist, get a full blood panel before supplementing.",
        })
    return {"symptoms": symptoms_text, "findings": findings}
