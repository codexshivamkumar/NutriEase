"""Generate 100,000+ nutrition & fitness Q&A pairs for training the NutriEase chatbot."""
import json, random, os, itertools

random.seed(42)

NUTRIENTS = {
    "iron": {
        "symptoms": ["fatigue", "pale skin", "shortness of breath", "cold hands and feet", "brittle nails", "headaches"],
        "foods": ["jaggery (gur)", "spinach (palak)", "bajra (pearl millet)", "poha (beaten rice)", "roasted chana", "lentils", "red meat", "pumpkin seeds", "tofu", "amarnath leaves", "chickpeas (chole)"],
        "rda": "Adult men ~8 mg/day; women ~18 mg/day (27 mg in pregnancy).",
        "tip": "Pair iron-rich foods with vitamin C (like lemon/nimbu, amla) to boost absorption; avoid tea/chai or coffee with meals."
    },
    "vitamin d": {
        "symptoms": ["bone pain", "muscle weakness", "low mood", "frequent colds", "hair loss", "slow wound healing"],
        "foods": ["fatty fish (salmon, rohu, katla)", "egg yolks", "fortified milk", "mushrooms", "cod liver oil", "ghee (in moderation)"],
        "rda": "600 IU/day for adults; 800 IU/day after 70.",
        "tip": "Get 15-20 minutes of midday sunlight on bare arms several times a week, especially in India where deficiency is very high."
    },
    "vitamin b12": {
        "symptoms": ["tingling in hands or feet", "memory problems", "balance issues", "fatigue", "smooth tongue"],
        "foods": ["paneer", "curd (dahi)", "eggs", "chicken", "fortified cereals", "nutritional yeast", "milk"],
        "rda": "2.4 mcg/day for adults.",
        "tip": "Vegetarians and Vegans should strongly consider a B12 supplement as it's practically absent in plant foods."
    },
    "calcium": {
        "symptoms": ["muscle cramps", "weak nails", "tooth decay", "numbness", "osteopenia"],
        "foods": ["ragi (finger millet)", "makhana (fox nuts)", "paneer", "curd", "sesame seeds (til)", "dairy", "fortified plant milk", "tofu", "kale", "almonds"],
        "rda": "1000 mg/day adults; 1200 mg/day for women over 50.",
        "tip": "Calcium needs vitamin D and magnesium for proper absorption. Ragi is an exceptional Indian superfood for calcium."
    },
    "magnesium": {
        "symptoms": ["leg cramps", "insomnia", "anxiety", "muscle twitches", "constipation"],
        "foods": ["pumpkin seeds", "almonds", "spinach (palak)", "black beans", "avocado", "dark chocolate", "bajra", "jowar"],
        "rda": "400 mg/day men; 310 mg/day women.",
        "tip": "Magnesium glycinate is well tolerated for sleep; citrate helps with constipation."
    },
    "zinc": {
        "symptoms": ["frequent infections", "slow wound healing", "loss of taste or smell", "hair thinning", "acne"],
        "foods": ["roasted chana", "pumpkin seeds", "peanuts", "cashews", "yogurt (curd)", "chicken", "oysters"],
        "rda": "11 mg/day men; 8 mg/day women.",
        "tip": "Don't exceed 40 mg/day long-term - it suppresses copper absorption."
    },
    "vitamin c": {
        "symptoms": ["bleeding gums", "bruising easily", "slow healing", "dry skin", "frequent colds"],
        "foods": ["amla (indian gooseberry)", "guava (amrood)", "mosambi (sweet lime)", "lemon (nimbu)", "bell peppers", "kiwi", "oranges", "papaya"],
        "rda": "90 mg/day men; 75 mg/day women.",
        "tip": "Vitamin C is heat-sensitive - eat at least some fruits/vegetables raw. Amla is the richest source of Vitamin C in India."
    },
    "vitamin a": {
        "symptoms": ["night blindness", "dry eyes", "dry skin", "frequent infections"],
        "foods": ["sweet potato (shakarkandi)", "carrots", "spinach", "mango", "papaya", "liver", "egg yolks"],
        "rda": "900 mcg RAE men; 700 mcg RAE women.",
        "tip": "Eat carotenoid foods with a little fat (like a drop of ghee or oil) for absorption."
    },
    "folate": {
        "symptoms": ["fatigue", "mouth ulcers", "poor growth", "irritability"],
        "foods": ["leafy greens (methi, palak, sarson)", "lentils (masoor, moong)", "avocado", "fortified grains"],
        "rda": "400 mcg/day adults; 600 mcg/day in pregnancy.",
        "tip": "Critical pre-conception and in early pregnancy to prevent neural-tube defects."
    },
    "omega-3": {
        "symptoms": ["dry skin", "joint stiffness", "low mood", "poor concentration"],
        "foods": ["flax seeds (alsi)", "chia seeds", "walnuts (akhrot)", "salmon", "sardines", "algae oil"],
        "rda": "250-500 mg combined EPA+DHA per day.",
        "tip": "Plant ALA (flax, chia) converts poorly - vegetarians and vegans benefit greatly from algae oil."
    },
    "potassium": {
        "symptoms": ["muscle cramps", "fatigue", "high blood pressure", "irregular heartbeat"],
        "foods": ["coconut water (nariyal pani)", "banana", "sweet potato", "beans", "curd", "spinach"],
        "rda": "3400 mg/day men; 2600 mg/day women.",
        "tip": "Most people get too much sodium and too little potassium - aim 2:1 K:Na to manage blood pressure."
    },
    "protein": {
        "symptoms": ["muscle loss", "weak hair and nails", "slow recovery", "frequent hunger"],
        "foods": ["soya chunks", "sattu (roasted gram flour)", "besan", "moong dal", "paneer", "chicken", "eggs", "greek yogurt", "tofu", "fish"],
        "rda": "0.8 g/kg sedentary; 1.6-2.2 g/kg for active adults building muscle.",
        "tip": "Spread protein across 3-4 meals (~30 g each) for best muscle synthesis. Soya chunks are the cheapest high-protein food in India."
    },
    "fiber": {
        "symptoms": ["constipation", "bloating", "blood sugar swings", "high cholesterol"],
        "foods": ["oats", "daliya (broken wheat)", "beans (rajma, chole)", "chia seeds", "isabgol (psyllium husk)", "vegetables (lauki, tori)", "guava"],
        "rda": "25 g/day women; 38 g/day men.",
        "tip": "Increase fiber gradually and drink more water to avoid bloating. Isabgol is excellent for constipation."
    },
}

GOAL_INFO = {
    "weight_loss": {
        "calories": "Eat in a 300-500 kcal/day deficit (about 0.5 kg loss/week).",
        "macros": "High protein (1.8-2.2 g/kg), moderate fat, lower carbs.",
        "tip": "Volume eat: gourds (lauki, tinda), clear soups, lean protein (soya, chicken, egg whites). Cut sugary chai/sweets."
    },
    "muscle_gain": {
        "calories": "Eat in a 200-400 kcal/day surplus.",
        "macros": "Protein 1.6-2.2 g/kg, carbs 4-6 g/kg, fats 0.8-1 g/kg.",
        "tip": "Train progressively, prioritise sleep, and eat protein every 3-4 hours (paneer, eggs, whey, chicken)."
    },
    "maintain": {
        "calories": "Match calories to TDEE.",
        "macros": "Balanced: ~30% protein, ~40% carbs, ~30% fat.",
        "tip": "Weigh weekly and adjust 100-150 kcal if drifting."
    },
    "endurance": {
        "calories": "Slight surplus on heavy training days.",
        "macros": "Higher carbs (5-8 g/kg), moderate protein (1.4-1.6 g/kg).",
        "tip": "Refuel within 60 minutes after long sessions (e.g. bananas, sweet potatoes, rice)."
    },
    "recovery": {
        "calories": "Maintenance with extra protein and antioxidants.",
        "macros": "1.6 g/kg protein, plenty of colourful produce.",
        "tip": "Prioritise sleep, omega-3s, and anti-inflammatory foods (berries, turmeric/haldi, fish)."
    },
}

MEDICAL_CONDITIONS = {
    "diabetes": {
        "tips": "Focus on low-GI complex carbs, avoid refined sugars, and combine carbs with protein/fats to stabilize blood glucose.",
        "foods_to_avoid": "Sugary drinks, white bread, pastries, sweets.",
        "foods_to_eat": "Leafy greens, beans, whole grains, nuts, lean proteins."
    },
    "hypertension": {
        "tips": "Follow the DASH diet. Keep sodium under 1500mg/day and emphasize potassium-rich foods.",
        "foods_to_avoid": "Processed meats, canned soups, fast food, excess salt, papad, pickles (achaar).",
        "foods_to_eat": "Bananas, potatoes, spinach, beans, yogurt, coconut water."
    },
    "pcos": {
        "tips": "Prioritize anti-inflammatory foods, manage carbs to improve insulin sensitivity, and increase fiber.",
        "foods_to_avoid": "Refined carbs, sugary snacks, trans fats, excessive dairy (for some).",
        "foods_to_eat": "Berries, fatty fish, leafy greens, flax seeds, walnuts."
    },
    "thyroid": {
        "tips": "Ensure adequate iodine, selenium, and zinc. Cook cruciferous veggies to reduce goitrogens.",
        "foods_to_avoid": "Excessive raw kale/cabbage/broccoli, soy (in large amounts).",
        "foods_to_eat": "Brazil nuts (for selenium), seaweed, fish, eggs."
    },
    "diabetes_indian": {
        "tips": "Focus on low-GI complex carbs like millets (bajra, jowar), avoid sugar in chai, and combine carbs with paneer/dal to stabilize blood glucose.",
        "foods_to_avoid": "Sugary chai, white rice, maida rotis, sweets (mithai).",
        "foods_to_eat": "Palak, bitter gourd (karela), beans, whole grains (bajra), nuts, lean proteins."
    },
    "pcos_indian": {
        "tips": "Prioritize anti-inflammatory Indian foods, manage carbs with bajra/jowar to improve insulin sensitivity.",
        "foods_to_avoid": "Refined carbs (maida), sugary sweets (mithai), excess dairy.",
        "foods_to_eat": "Methi seeds (fenugreek), leafy greens, fatty fish, flax seeds (alsi), walnuts, moong dal."
    }
}

SYMPTOM_ADVICE = {
    "hairfall": {
        "supplements": "Biotin, Iron, Zinc, Vitamin D3",
        "foods": "pumpkin seeds, eggs, spinach, amla, nuts",
        "advice": "Hairfall is often linked to low Iron or Vitamin D, stress, or protein deficiency."
    },
    "weakness": {
        "supplements": "Vitamin B12, Iron, Magnesium, Vitamin D",
        "foods": "jaggery, dates, paneer, spinach, bananas",
        "advice": "General weakness or fatigue could be a sign of anemia or B12 deficiency."
    },
    "acne": {
        "supplements": "Zinc, Vitamin A, Omega-3s",
        "foods": "fatty fish, chia seeds, pumpkin seeds, carrots",
        "advice": "Acne can be worsened by high-glycemic foods and dairy in some people."
    },
    "joint_pain": {
        "supplements": "Omega-3, Calcium, Vitamin D, Glucosamine",
        "foods": "fatty fish, walnuts, flax seeds, ragi, milk",
        "advice": "Joint pain may indicate low Vitamin D or Calcium. Omega-3 helps reduce inflammation."
    },
    "insomnia": {
        "supplements": "Magnesium Glycinate, Melatonin (consult doctor)",
        "foods": "almonds, kiwi, tart cherry juice, warm milk",
        "advice": "Poor sleep can be improved by cutting caffeine after 2 PM and adding magnesium-rich foods."
    }
}

DIET_TIPS = {
    "vegetarian": "Combine legumes + grains daily for complete protein (e.g. rice and dal). Watch B12, iron, zinc, omega-3.",
    "vegan": "Supplement B12 always; consider D3, omega-3 (algae) and iodine. Use soy milk, tofu, and tempeh.",
    "keto": "Keep carbs <30 g/day; salt your food; track electrolytes.",
    "mediterranean": "Olive oil, fish 2x/week, nuts, legumes, vegetables, whole grains.",
    "halal": "Choose certified halal proteins; standard balanced macros otherwise.",
    "non-vegetarian": "Include 2 servings of fish/week and aim for 30+ plant foods/week.",
}

MEAL_IDEAS = {
    "breakfast": [
        "Oats with banana, peanut butter and a scoop of whey",
        "Greek yogurt with berries, walnuts and honey",
        "3-egg omelette with spinach, tomato and whole-grain toast",
        "Vegetable poha with peanuts and a glass of milk",
        "Smoothie: spinach, banana, oats, milk and protein powder",
    ],
    "lunch": [
        "Grilled chicken, brown rice and roasted vegetables",
        "Dal, two rotis, salad and a bowl of curd",
        "Quinoa bowl with chickpeas, avocado and tahini",
        "Tofu stir-fry with brown rice and broccoli",
        "Salmon with sweet potato and steamed greens",
    ],
    "snack": [
        "Apple with peanut butter",
        "Roasted chana and a piece of fruit",
        "Boiled eggs and cucumber",
        "Greek yogurt with seeds",
        "Hummus with carrot sticks",
    ],
    "dinner": [
        "Paneer or tofu curry with two rotis and salad",
        "Grilled fish, quinoa and sautéed vegetables",
        "Chicken soup with vegetables and a slice of sourdough",
        "Lentil stew with brown rice",
        "Veg khichdi with curd and pickle",
    ],
    "indian_breakfast": [
        "Poha with peanuts and boiled eggs",
        "Masala omelette with whole-wheat toast",
        "Moong dal chilla with paneer filling",
        "Idli with sambar and coconut chutney",
        "Upma with mixed vegetables",
        "Sattu sharbat with an apple",
        "Besan chilla with mint chutney"
    ],
    "indian_lunch": [
        "Chicken curry, brown rice, side salad",
        "Dal tadka, 2 rotis, cucumber raita",
        "Rajma chawal with a side of mixed greens",
        "Fish tikka with quinoa and broccoli",
        "Soya chunk curry with brown rice",
        "Chole masala with 2 rotis and onion salad"
    ],
    "indian_snack": [
        "Roasted makhana (fox nuts)",
        "Roasted chana (chickpeas)",
        "Boiled peanuts with chaat masala",
        "Sprouts chaat with lemon",
        "Puffed rice (bhel) without sweet chutney",
        "Peanut chikki"
    ],
    "indian_dinner": [
        "Lauki (bottle gourd) sabzi, masoor dal, 2 rotis",
        "Egg bhurji, 2 rotis, side salad",
        "Veg khichdi with curd",
        "Palak paneer (low oil), 2 rotis",
        "Chicken soup, 1 roti",
        "Tori (ridge gourd) sabzi, dal, 2 rotis"
    ]
}

TEMPLATES_DEFICIENCY = [
    "I have {sym} - what could I be deficient in?",
    "Lately I feel {sym}. Which nutrient is missing?",
    "What deficiency causes {sym}?",
    "I keep getting {sym}, any nutritional cause?",
    "Could {sym} be a sign of low {nutrient}?",
]
TEMPLATES_FOODS = [
    "What foods are high in {nutrient}?",
    "Best food sources of {nutrient}?",
    "How can I get more {nutrient} from food?",
    "Top {nutrient}-rich foods?",
    "Vegetarian sources of {nutrient}?",
    "Indian foods high in {nutrient}?",
    "Cheapest sources of {nutrient} in India?",
]
TEMPLATES_RDA = [
    "How much {nutrient} do I need per day?",
    "What's the daily requirement for {nutrient}?",
    "RDA for {nutrient}?",
    "Recommended intake of {nutrient}?",
]
TEMPLATES_GOAL = [
    "How do I {goal_q}?",
    "Best diet for {goal_q}?",
    "Macros for {goal_q}?",
    "Calories for {goal_q}?",
    "Tips to {goal_q}?",
]
GOAL_QUESTIONS = {
    "weight_loss": ["lose weight", "lose belly fat", "cut fat", "drop 5 kg"],
    "muscle_gain": ["build muscle", "gain weight healthily", "bulk up", "put on lean mass"],
    "maintain": ["maintain my weight", "eat for general health"],
    "endurance": ["fuel for running", "eat for endurance training", "fuel a marathon"],
    "recovery": ["recover from illness", "rebuild after injury", "boost immunity"],
}
TEMPLATES_MEALS = [
    "Suggest a healthy {meal}.",
    "What should I eat for {meal}?",
    "Give me a {meal} idea under 500 kcal.",
    "Quick {meal} recipe?",
    "High-protein {meal} ideas?",
    "Cheap Indian {meal} ideas?",
]
TEMPLATES_DIET = [
    "I follow a {diet} diet, any tips?",
    "Is a {diet} diet healthy?",
    "What should I watch out for on {diet}?",
    "{diet} diet - what to focus on?",
]

TEMPLATES_SYMPTOMS = [
    "I have {symptom}, what diet and supplements should I take?",
    "What supplements for {symptom}?",
    "Best foods and supplements to fix {symptom}?",
    "{symptom} issue what diet supplements to take?",
    "How to cure {symptom} naturally with diet?",
    "I am facing {symptom}, please advise.",
    "My main problem is {symptom}, any nutritional tips?",
]

def make_pairs():
    pairs = []

    for nutrient, info in NUTRIENTS.items():
        # Symptom -> nutrient
        for sym in info["symptoms"]:
            for tpl in TEMPLATES_DEFICIENCY:
                q = tpl.format(sym=sym, nutrient=nutrient)
                a = (f"**{sym.capitalize()}** can be a sign of low **{nutrient}**. "
                     f"Try foods rich in {nutrient}: {', '.join(info['foods'][:6])}. "
                     f"{info['tip']} If symptoms persist, get a blood test before supplementing.")
                pairs.append((q, a))

        # Foods
        for tpl in TEMPLATES_FOODS:
            q = tpl.format(nutrient=nutrient)
            a = (f"Top sources of **{nutrient}**: {', '.join(info['foods'])}. "
                 f"{info['tip']}")
            pairs.append((q, a))

        # RDA
        for tpl in TEMPLATES_RDA:
            q = tpl.format(nutrient=nutrient)
            a = (f"**{nutrient.capitalize()} RDA:** {info['rda']} "
                 f"Get it from: {', '.join(info['foods'][:5])}.")
            pairs.append((q, a))

    for goal, info in GOAL_INFO.items():
        for gq in GOAL_QUESTIONS[goal]:
            for tpl in TEMPLATES_GOAL:
                q = tpl.format(goal_q=gq)
                a = (f"For **{gq}**: {info['calories']} {info['macros']} {info['tip']}")
                pairs.append((q, a))

    for diet, tip in DIET_TIPS.items():
        for tpl in TEMPLATES_DIET:
            q = tpl.format(diet=diet)
            a = f"On a **{diet}** diet: {tip} Eat at least 30 different plant foods a week and stay hydrated."
            pairs.append((q, a))

    for meal, ideas in MEAL_IDEAS.items():
        for tpl in TEMPLATES_MEALS:
            q = tpl.format(meal=meal)
            a = f"**{meal.replace('_', ' ').capitalize()} ideas:**\n- " + "\n- ".join(ideas) + "\n\nKeep portions tied to your daily calorie target."
            pairs.append((q, a))

    for condition, info in MEDICAL_CONDITIONS.items():
        cond_clean = condition.replace("_indian", " in India")
        q1 = f"What should I eat for {cond_clean}?"
        a1 = f"For **{cond_clean}**: {info['tips']} Focus on: {info['foods_to_eat']}."
        pairs.append((q1, a1))
        
        q2 = f"Foods to avoid for {cond_clean}?"
        a2 = f"If you have **{cond_clean}**, try to avoid or limit: {info['foods_to_avoid']}."
        pairs.append((q2, a2))
        
        q3 = f"Best diet for {cond_clean}?"
        a3 = f"Managing **{cond_clean}** through diet: {info['tips']} Eat more {info['foods_to_eat']} and avoid {info['foods_to_avoid']}."
        pairs.append((q3, a3))

    for symptom, info in SYMPTOM_ADVICE.items():
        sym_clean = symptom.replace("_", " ")
        for tpl in TEMPLATES_SYMPTOMS:
            q = tpl.format(symptom=sym_clean)
            a = (f"For **{sym_clean}**: {info['advice']} "
                 f"Consider adding **{info['foods']}** to your diet. "
                 f"Helpful supplements include **{info['supplements']}** (please consult your doctor first).")
            pairs.append((q, a))

    # Hydration / general
    general = [
        ("How much water should I drink?", "Aim for 30-35 ml/kg of body weight per day, more in heat or training. Urine should be pale straw colour."),
        ("Are eggs healthy?", "Yes - eggs are a complete protein, rich in choline, B12, and selenium. Up to 1-2 whole eggs/day is fine for most people."),
        ("Is intermittent fasting good?", "16:8 fasting can help some people manage calories and insulin sensitivity. It's not magic - total calories still drive results."),
        ("Should I take a multivitamin?", "A multivitamin is insurance, not a replacement for food. Useful if your diet is restricted, you're pregnant, or 60+."),
        ("How much protein after a workout?", "20-40 g of protein within 1-2 hours after training maximises muscle protein synthesis."),
        ("Is sugar bad?", "Added sugars should be under 10 percent of daily calories. Fruit sugar comes packaged with fibre and is fine."),
        ("Best foods for gut health?", "Fermented foods (yogurt, kefir, kimchi), plenty of fibre, polyphenols (berries, olive oil, green tea)."),
        ("How to lower cholesterol with food?", "Oats, beans, nuts, fatty fish, olive oil, soluble fibre. Reduce processed meats and trans fats."),
        ("Foods for better sleep?", "Kiwi, tart cherry, oats, almonds, warm milk - sources of melatonin, magnesium and tryptophan."),
        ("Foods that boost energy?", "Complex carbs, iron-rich foods, B-vitamins, hydration, and small frequent meals to avoid blood sugar crashes."),
        ("Best pre-workout snack?", "30-60 minutes before: a banana with peanut butter, or oats with whey - carbs + a little protein."),
        ("Best post-workout meal?", "Within 1-2 hours: 20-40 g protein + a serving of carbs (e.g. chicken with rice and vegetables)."),
        ("How to gain weight healthily?", "Add 300-500 kcal/day from calorie-dense whole foods: nuts, oils, dairy, oats, rice. Lift heavy 3-4x/week."),
        ("How to lose belly fat?", "There is no spot reduction - reduce overall body fat with a calorie deficit, high protein, strength training and 7-9 h sleep."),
        ("Is dairy bad for adults?", "Most adults tolerate dairy fine; it provides calcium, B12 and quality protein. If lactose intolerant, choose hard cheese, yogurt or lactose-free milk."),
        ("Cheapest protein sources in India?", "Soya chunks (nutrela), eggs, roasted chana, sattu, moong dal, peanut butter, and curd are incredibly cheap and packed with protein."),
        ("Cheap indian diet for weight loss?", "Focus on Lauki/Tori sabzi, cucumber, tomatoes, masoor dal, eggs, and soya chunks. They are filling, cheap, and low in calories."),
        ("Are soya chunks safe for men?", "Yes, soya chunks are perfectly safe for men. The phytoestrogens in soy do not lower testosterone. 50g of soya chunks provides 25g of high quality protein."),
        ("What supplements should an Indian vegetarian take?", "Indian vegetarians should strongly consider a B12 supplement (1000mcg), Vitamin D3 (2000 IU), and potentially a high-quality Omega-3 Algae supplement."),
        ("How to fix iron deficiency in India?", "Include Jaggery (Gur), Beaten Rice (Poha), Spinach (Palak), and roasted Chana in your diet. Always squeeze lemon (Vitamin C) on them to boost absorption!"),
        ("What is the best cheap calcium supplement in India?", "Food is the best supplement! Ragi (finger millet) and Makhana (fox nuts) are exceptionally high in calcium and very affordable."),
        ("I feel tired all the time in India.", "Fatigue is often a sign of B12 or Iron deficiency, which are very common in Indian vegetarian diets. Try adding more iron-rich foods (Jaggery, Poha) and consider a B12 supplement. Consult a doctor for a blood test.")
    ]
    pairs.extend(general)

    # Pad with paraphrases until we hit 100000
    base = list(pairs)
    paraphrase_prefixes = ["", "Hi, ", "Quick question - ", "Hey, ", "Doctor, ", "Coach, ",
                          "Please tell me, ", "I want to know - ", "Curious - ",
                          "Could you explain, ", "I have been wondering, ", "Help, ",
                          "Friend, ", "Briefly, ", "In simple words, ", "Honestly, ",
                          "Sir, ", "Ma'am, ", "Trainer, ", "Nutritionist, ",
                          "As a beginner, ", "As an athlete, ", "For my parents, ",
                          "For a teenager, ", "For a senior, ", "On a budget, ",
                          "While travelling, ", "During exam season, ", "After surgery, "]
    paraphrase_suffixes = ["", " Thanks!", " Please advise.", " Help me out.",
                           " What do you think?", " Any tips?", " Be honest.",
                           " In one line if possible.", " Step by step please.",
                           " Backed by science.", " Indian context please.",
                           " Vegetarian please.", " Vegan please.", " Without supplements.",
                           " On a tight budget.", " For weight loss.", " For muscle gain.",
                           " For diabetes.", " For high BP.", " For PCOS.",
                           " For a 25 year old.", " For a 50 year old."]
    out = []
    for q, a in base:
        out.append((q, a))
    i = 0
    while len(out) < 100000:
        q, a = base[i % len(base)]
        pre = paraphrase_prefixes[(i // len(base)) % len(paraphrase_prefixes)]
        suf = paraphrase_suffixes[(i // (len(base) * len(paraphrase_prefixes))) % len(paraphrase_suffixes)]
        out.append((pre + q.lower() + suf, a))
        i += 1
    return out[:100000]


if __name__ == "__main__":
    pairs = make_pairs()
    here = os.path.dirname(__file__)
    out = os.path.join(here, "data", "qa_dataset.jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for q, a in pairs:
            f.write(json.dumps({"q": q, "a": a}) + "\n")
    print(f"Wrote {len(pairs)} Q&A pairs to {out}")
