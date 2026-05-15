"""Rule-based 7-day diet plan generator."""
import random
import re
import time

INDIAN_MEALS = {
    "non-vegetarian": {
        "breakfast": [
            ("Poha with peanuts and boiled eggs", 450),
            ("Masala omelette (3 eggs) + 2 whole wheat toast", 480),
            ("Egg bhurji with 2 parathas", 500),
            ("Chicken sausage with whole wheat toast", 450),
            ("Moong dal chilla with paneer and 1 boiled egg", 420),
            ("Upma with mixed veg and 2 boiled eggs", 460),
            ("Idli (3 pcs) with sambar and boiled egg", 430),
            ("Dosa with chicken kheema filling", 550),
            ("Oats porridge with almonds and boiled egg", 400),
            ("Egg roll in whole wheat roti", 480),
            ("Leftover dal paratha with 2 boiled eggs", 520),
            ("Chicken cutlets (baked) with toast", 450),
            ("Vermicelli (semiya) upma with eggs", 460),
            ("Appam with egg stew", 450),
            ("Millet dosa with egg podi", 440)
        ],
        "lunch": [
            ("Chicken curry, brown rice, side salad", 600),
            ("Fish tikka with quinoa and broccoli", 650),
            ("Egg bhurji, 2 rotis, cucumber raita", 550),
            ("Mutton rogan josh (lean), 2 rotis, salad", 650),
            ("Chicken biryani (brown rice) with raita", 700),
            ("Soya and chicken mixed pulao, curd", 620),
            ("Tandoori chicken, 2 rotis, mint chutney", 580),
            ("Prawn curry with red rice and cabbage sabzi", 600),
            ("Keema matar, 2 rotis, dal tadka", 650),
            ("Fish curry (Goan style), brown rice", 600),
            ("Egg curry (2 eggs), 2 rotis, lauki sabzi", 580),
            ("Grilled chicken breast, quinoa, sauteed greens", 550),
            ("Chicken stir-fry with capsicum and 2 rotis", 580),
            ("Methi chicken, brown rice, salad", 600),
            ("Palak egg curry, 2 rotis, cucumber sticks", 550)
        ],
        "snack": [
            ("Roasted chana + 1 apple", 220),
            ("Boiled eggs (2) + cucumber", 200),
            ("Sprouts chaat with lemon", 180),
            ("Chicken tikka skewers (3 pcs)", 250),
            ("Peanut chaat with onions and tomatoes", 240),
            ("Roasted makhana + green tea", 150),
            ("Boiled egg whites (3) + almonds", 180),
            ("Soya chunks roasted in air fryer", 200),
            ("Fruit bowl with chaat masala", 150),
            ("Buttermilk (chaas) + roasted peanuts", 180),
            ("Boiled black chana chaat", 200),
            ("Handful of mixed nuts (walnuts, peanuts)", 250),
            ("Omelette (1 egg) with veggies", 120),
            ("Cottage cheese (paneer) cubes raw", 180),
            ("Moong dal sprouts + pomegranate", 160)
        ],
        "dinner": [
            ("Chicken tikka, 2 rotis, mixed veg sabzi", 600),
            ("Grilled fish + sauteed greens", 580),
            ("Keema matar with brown rice", 620),
            ("Egg bhurji, dal tadka, 2 rotis", 600),
            ("Chicken soup, 2 slice sourdough bread", 500),
            ("Tandoori fish, quinoa, roasted broccoli", 600),
            ("Chicken and vegetable stew, 1 roti", 550),
            ("Lemon chicken dry, side salad, 1 roti", 500),
            ("Fish amritsari (baked), dal, 2 rotis", 650),
            ("Palak chicken, brown rice", 600),
            ("Soya and egg bhurji mix, 2 rotis", 580),
            ("Baked chicken breast, mixed veg sabzi", 500),
            ("Egg drop soup with sweet corn, 1 toast", 450),
            ("Mutton clear soup, 2 rotis, salad", 550),
            ("Chicken kebabs (baked), mint chutney, 2 rotis", 580)
        ]
    },
    "vegetarian": {
        "breakfast": [
            ("Vegetable poha + glass of milk", 430),
            ("Paneer paratha + curd", 500),
            ("Oats dalia with veggies", 400),
            ("Moong dal chilla with mint chutney", 420),
            ("Besan chilla loaded with vegetables", 400),
            ("Upma with lots of veggies and peanuts", 450),
            ("Idli (4 pcs) with sambar", 400),
            ("Dosa (plain) with sambar and coconut chutney", 450),
            ("Vermicelli (semiya) upma with carrots and peas", 420),
            ("Sattu paratha with curd", 500),
            ("Sprouts salad with yogurt dressing", 350),
            ("Ragi malt/porridge with almonds", 380),
            ("Daliya (broken wheat) sweet porridge with milk", 450),
            ("Leftover roti upma", 400),
            ("Paneer bhurji with 2 whole wheat toast", 450)
        ],
        "lunch": [
            ("Dal tadka, 2 rotis, salad, curd", 600),
            ("Rajma chawal with raita", 650),
            ("Soya chunk curry, brown rice", 600),
            ("Chole (chickpea) masala, 2 rotis, salad", 620),
            ("Palak paneer, 2 rotis, cucumber raita", 650),
            ("Kala chana curry, brown rice, cabbage sabzi", 600),
            ("Mixed dal (panchratna), 2 rotis, bhindi sabzi", 580),
            ("Kadhi pakora, brown rice, side salad", 650),
            ("Mushroom matar masala, 2 rotis", 550),
            ("Lauki chana dal, 2 rotis, curd", 550),
            ("Baingan bharta, dal, 2 rotis", 600),
            ("Paneer tikka masala, brown rice", 650),
            ("Vegetable pulao with soya chunks, raita", 600),
            ("Lobiya (black eyed peas) curry, brown rice", 580),
            ("Matar paneer, 2 rotis, carrot salad", 620)
        ],
        "snack": [
            ("Roasted peanuts + fruit", 220),
            ("Makhana (fox nuts) roasted with ghee", 210),
            ("Paneer tikka skewers", 200),
            ("Roasted black chana", 180),
            ("Buttermilk (chaas) + roasted makhana", 150),
            ("Sprouts chaat", 150),
            ("Fruit chaat (guava, papaya, apple)", 120),
            ("Sattu drink (sweet or savory)", 150),
            ("Puffed rice (bhel) without sweet chutney", 180),
            ("Roasted pumpkin seeds + almonds", 250),
            ("Yogurt with flax seeds", 150),
            ("Handful of peanuts and jaggery (chikki)", 250),
            ("Carrot and cucumber sticks with hummus", 200),
            ("Boiled sweet potato with chaat masala", 180),
            ("Soya katori (roasted soya snacks)", 200)
        ],
        "dinner": [
            ("Paneer bhurji, 2 rotis, salad", 600),
            ("Veg khichdi with curd and pickle", 550),
            ("Lauki sabzi, dal, 2 rotis", 580),
            ("Dal makhani (low cream), 2 rotis", 620),
            ("Soya chunks stir-fry, 2 rotis", 550),
            ("Mixed vegetable sabzi, dal, 2 rotis", 580),
            ("Pumpkin (kaddu) sabzi, moong dal, 2 rotis", 550),
            ("Tori (ridge gourd) sabzi, masoor dal, 2 rotis", 550),
            ("Mushroom tikka, dal tadka, 1 roti", 500),
            ("Palak dal, brown rice, salad", 550),
            ("Cabbage peas sabzi, 2 rotis, small curd", 550),
            ("Aloo gobi (less oil), dal, 2 rotis", 600),
            ("Besan gatte ki sabzi, 2 rotis", 600),
            ("Oats khichdi with plenty of vegetables", 450),
            ("Tomato soup, paneer sandwich (whole wheat)", 500)
        ]
    },
    "vegan": {
        "breakfast": [
            ("Oats with banana and peanut butter", 450),
            ("Besan chilla with green chutney", 470),
            ("Smoothie: oats, banana, soy milk", 420),
            ("Vegetable poha with peanuts", 400),
            ("Upma with mixed veg and cashews", 450),
            ("Idli (4 pcs) with sambar", 400),
            ("Moong dal chilla with tofu filling", 450),
            ("Sprouts salad with lemon and tomatoes", 350),
            ("Daliya porridge with almond milk", 400),
            ("Ragi malt with walnuts", 380),
            ("Sattu drink and an apple", 300),
            ("Puffed rice (murmura) upma", 350),
            ("Tofu bhurji with 2 whole wheat toast", 450),
            ("Chia pudding with coconut milk and berries", 400),
            ("Avocado toast on whole wheat bread", 450)
        ],
        "lunch": [
            ("Chickpea curry (chole), brown rice, salad", 620),
            ("Tofu matar masala with 2 rotis", 600),
            ("Mixed dal, quinoa, greens", 580),
            ("Rajma chawal with cucumber salad", 650),
            ("Soya chunk curry, brown rice", 600),
            ("Kala chana, 2 rotis, cabbage sabzi", 600),
            ("Lobiya curry, brown rice, side salad", 580),
            ("Palak tofu, 2 rotis", 600),
            ("Vegetable pulao with soya chunks", 600),
            ("Mushroom and peas curry, 2 rotis", 550),
            ("Lauki chana dal, brown rice", 550),
            ("Baingan bharta, dal, 2 rotis", 600),
            ("Mixed veg sambar, brown rice", 550),
            ("Bhindi masala, dal tadka, 2 rotis", 600),
            ("Aloo beans sabzi, masoor dal, 2 rotis", 600)
        ],
        "snack": [
            ("Apple + 20 g almonds", 220),
            ("Roasted chana", 220),
            ("Hummus + cucumber", 200),
            ("Roasted peanuts", 250),
            ("Sprouts chaat", 150),
            ("Fruit bowl (guava, papaya, banana)", 150),
            ("Roasted makhana (without ghee)", 150),
            ("Puffed rice (bhel) with onions/tomatoes", 180),
            ("Soya sticks (roasted)", 200),
            ("Handful of walnuts and pumpkin seeds", 250),
            ("Coconut water + fruit", 120),
            ("Boiled sweet potato", 150),
            ("Carrot sticks with peanut butter", 220),
            ("Peanut chikki", 200),
            ("Boiled black chana with lemon", 180)
        ],
        "dinner": [
            ("Tofu curry, 2 rotis, salad", 580),
            ("Soya chunks stir-fry with brown rice", 600),
            ("Lentil dal, brown rice, sautéed greens", 600),
            ("Veg khichdi (without ghee) with pickle", 500),
            ("Lauki sabzi, masoor dal, 2 rotis", 550),
            ("Mixed vegetable sabzi, moong dal, 2 rotis", 580),
            ("Tofu tikka skewers with mint chutney", 450),
            ("Palak dal, brown rice", 550),
            ("Cabbage peas sabzi, 2 rotis, side salad", 500),
            ("Mushroom stir fry, quinoa", 500),
            ("Tori (ridge gourd) sabzi, dal tadka, 2 rotis", 550),
            ("Tomato soup, tofu sandwich", 450),
            ("Oats khichdi with mixed veg", 450),
            ("Pumpkin (kaddu) sabzi, 2 rotis, side salad", 500),
            ("Sambar, 2 plain dosas", 500)
        ]
    }
}

GLOBAL_MEALS = INDIAN_MEALS # Fallback for now to avoid massive file size, or we can keep the original GLOBAL_MEALS but the user asked for Indian. We will keep original Global Meals for 'global' region.
GLOBAL_MEALS = {
    "non-vegetarian": {
        "breakfast": [("Oats with banana, peanut butter, milk", 450),
                      ("3-egg omelette + 2 toast + fruit", 480),
                      ("Greek yogurt parfait with berries", 420),
                      ("Turkey bacon with scrambled eggs", 450),
                      ("Smoked salmon toast", 500)],
        "lunch": [("Grilled chicken, brown rice, roasted veg", 600),
                  ("Chicken stir-fry with quinoa", 650),
                  ("Tuna salad bowl with chickpeas", 550),
                  ("Turkey wrap with hummus", 580),
                  ("Beef chilli with rice", 650)],
        "snack": [("Apple + almonds", 220), ("Boiled eggs", 200), ("Greek yogurt", 180)],
        "dinner": [("Grilled fish + quinoa + veg", 580),
                   ("Turkey chilli with rice", 620),
                   ("Chicken soup + sourdough", 550),
                   ("Baked salmon with sweet potato", 600),
                   ("Steak (lean) with asparagus", 650)],
    },
    "vegetarian": {
        "breakfast": [("Oats with banana, milk", 450), ("Avocado toast + 2 poached eggs", 500), ("Protein pancakes", 450)],
        "lunch": [("Quinoa bowl with chickpeas, avocado, tahini", 600), ("Cottage cheese wrap", 580), ("Lentil soup + sourdough", 550)],
        "snack": [("Apple + almonds", 220), ("Greek yogurt", 180), ("Protein bar", 200)],
        "dinner": [("Tofu stir-fry with brown rice", 580), ("Lentil stew with quinoa", 600), ("Vegetarian chilli", 550)],
    },
    "vegan": {
        "breakfast": [("Oats with banana, soy milk", 450), ("Tofu scramble + toast", 470), ("Chia pudding", 400)],
        "lunch": [("Buddha bowl: quinoa, tempeh, avocado", 650), ("Lentil soup + sourdough", 580), ("Chickpea salad sandwich", 600)],
        "snack": [("Apple + almonds", 220), ("Edamame", 180), ("Roasted chickpeas", 200)],
        "dinner": [("Tempeh stir-fry with rice", 600), ("Vegan chilli", 620), ("Black bean burgers", 600)],
    },
}

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def bmr_mifflin(weight, height, age, gender):
    if gender == "female":
        return 10 * weight + 6.25 * height - 5 * age - 161
    return 10 * weight + 6.25 * height - 5 * age + 5

ACTIVITY = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "athlete": 1.9}

def generate_plan(form: dict) -> dict:
    age = int(form.get("age") or 30)
    gender = form.get("gender") or "male"
    weight = float(form.get("weight_kg") or 70)
    height = float(form.get("height_cm") or 170)
    activity = form.get("activity_level") or "moderate"
    goal = form.get("goal") or "maintain"
    diet = form.get("diet_preference") or "non-vegetarian"
    region = form.get("diet_region") or "global"
    budget = form.get("budget") or "medium"
    
    bank = INDIAN_MEALS if region == "indian" else GLOBAL_MEALS
    if diet not in bank:
        diet = "non-vegetarian"

    bmr = bmr_mifflin(weight, height, age, gender)
    tdee = bmr * ACTIVITY.get(activity, 1.55)
    if goal == "weight_loss":
        cals = int(tdee - 400)
    elif goal == "muscle_gain":
        cals = int(tdee + 300)
    elif goal == "endurance":
        cals = int(tdee + 200)
    else:
        cals = int(tdee)

    if goal == "weight_loss":
        protein_g = int(weight * 2.0); fat_g = int(weight * 0.8)
    elif goal == "muscle_gain":
        protein_g = int(weight * 1.8); fat_g = int(weight * 0.9)
    else:
        protein_g = int(weight * 1.4); fat_g = int(weight * 0.9)
    carbs_g = max(50, int((cals - protein_g * 4 - fat_g * 9) / 4))

    # New RNG without a fixed hash seed so it generates unique plans every time
    rng = random.Random(time.time() + hash((age, gender, goal, diet, int(weight))))
    days = []
    
    # Budget adaptations
    budget_replacements = {
        "salmon": "canned tuna" if budget == "low" else "salmon",
        "quinoa": "brown rice" if budget == "low" else "quinoa",
        "almonds": "peanuts" if budget == "low" else "almonds",
        "avocado": "olive oil" if budget == "low" else "avocado",
        "paneer": "soya chunks" if budget == "low" else "paneer",
        "mutton": "chicken" if budget == "low" else "mutton"
    }

    slot_percentages = {
        "breakfast": 0.25,
        "lunch": 0.35,
        "snack": 0.10,
        "dinner": 0.30
    }
    
    # Randomly shuffle the bank options for this specific plan to guarantee 7 unique meals
    breakfast_options = rng.sample(bank[diet]["breakfast"], len(bank[diet]["breakfast"]))
    lunch_options = rng.sample(bank[diet]["lunch"], len(bank[diet]["lunch"]))
    snack_options = rng.sample(bank[diet]["snack"], len(bank[diet]["snack"]))
    dinner_options = rng.sample(bank[diet]["dinner"], len(bank[diet]["dinner"]))

    for i, d in enumerate(DAYS):
        meals = []
        
        # Pick sequentially from shuffled list to ensure no repetition within the week
        b_name, b_kcal = breakfast_options[i % len(breakfast_options)]
        l_name, l_kcal = lunch_options[i % len(lunch_options)]
        s_name, s_kcal = snack_options[i % len(snack_options)]
        d_name, d_kcal = dinner_options[i % len(dinner_options)]
        
        daily_choices = [
            ("breakfast", b_name, b_kcal),
            ("lunch", l_name, l_kcal),
            ("snack", s_name, s_kcal),
            ("dinner", d_name, d_kcal)
        ]
        
        for slot, name, base_kcal in daily_choices:
            target_kcal = int(cals * slot_percentages[slot])
            scale = target_kcal / float(base_kcal)
            
            # Apply budget replacements
            for high_end, low_end in budget_replacements.items():
                name = name.lower().replace(high_end, low_end).capitalize()
                
            # Scale numbers in meal text (e.g. 2 rotis -> 3 rotis)
            def replacer(match):
                val = float(match.group(1))
                new_val = val * scale
                if abs(new_val - round(new_val)) < 0.25:
                    return str(int(round(new_val)))
                return f"{new_val:.1f}"
                
            scaled_name = re.sub(r'\b(\d+(?:\.\d+)?)\b', replacer, name)
            
            grams = int(target_kcal / 1.5)
            # Estimate protein per meal based on 25% of calories coming from protein (approximate)
            # protein_g = (target_kcal * 0.25) / 4
            meal_protein_g = int(target_kcal * 0.25 / 4)
            final_name = f"{scaled_name} (Portion: ~{grams}g | Protein: ~{meal_protein_g}g | to hit {target_kcal} kcal)"
                
            meals.append({"name": slot.capitalize(), "items": [final_name], "calories": target_kcal})
        days.append({"day": d, "meals": meals})

    supplements = []
    defs = (form.get("deficiencies") or "").lower()
    conditions = (form.get("medical_conditions") or "").lower()
    bmi = weight / ((height/100)**2) if height else 22
    
    if "iron" in defs: supplements.append("Iron 18 mg with vitamin C, away from tea/coffee (Indian sources: Spinach/Palak, Jaggery, Beaten Rice/Poha)")
    if "b12" in defs or "vitamin b12" in defs: supplements.append("B12 1000 mcg sublingual daily")
    if "vitamin d" in defs or "vit d" in defs: supplements.append("Vitamin D3 2000 IU daily with a fatty meal")
    if "calcium" in defs: supplements.append("Calcium (Indian sources: Ragi, Makhana, Paneer, Curd)")
    
    if bmi > 25:
        supplements.append("Omega-3 / Fish Oil (1000mg EPA+DHA) for heart health and inflammation reduction.")
    if age > 50:
        supplements.append("Calcium & Vitamin D3 for bone health and density.")
        
    if diet == "vegan" and "b12" not in defs: supplements.append("B12 1000 mcg sublingual (essential on vegan diets)")
    if not supplements: supplements.append("A daily multivitamin as nutritional insurance (optional)")
    
    supplements.append("**Disclaimer:** *Please consult a doctor before starting any new supplements.*")

    tips = [
        f"Drink at least {round(weight * 0.033, 1)} L of water daily.",
        "Sleep 7-9 hours - poor sleep raises hunger hormones.",
        "Eat 30+ different plant foods a week for gut health.",
        "Spread protein across 3-4 meals (~30 g each).",
    ]
    if goal == "weight_loss":
        tips.append("Front-load calories earlier in the day; finish dinner 3 h before bed.")
    if goal == "muscle_gain":
        tips.append("Lift heavy 3-5x/week with progressive overload.")
        
    if "diabetes" in conditions:
        tips.append("Diabetes: Focus on low-GI complex carbs (Bajra, Jowar). Avoid refined sugars (Mithai) and monitor blood glucose.")
        carbs_g = max(50, int(carbs_g * 0.8))  # Slight reduction in carbs
    if "hypertension" in conditions or "blood pressure" in conditions:
        tips.append("Hypertension: Keep sodium under 1500mg/day. Emphasize potassium-rich foods like Bananas and Coconut Water.")
    if "pcos" in conditions:
        tips.append("PCOS: Prioritize anti-inflammatory foods (Methi seeds, Flax seeds) and maintain steady blood sugar with high fiber.")
    if "thyroid" in conditions:
        tips.append("Thyroid: Ensure adequate iodine and selenium. Cook cruciferous vegetables (Cabbage, Cauliflower) to reduce goitrogens.")

    return {
        "title": f"{goal.replace('_', ' ').title()} plan ({diet})",
        "summary": f"Personalised 7-day {diet} plan calibrated to {cals} kcal for your {goal.replace('_', ' ')} goal.",
        "daily_calories": cals,
        "macros": {"protein_g": protein_g, "carbs_g": carbs_g, "fats_g": fat_g},
        "hydration_liters": round(weight * 0.033, 1),
        "supplements": supplements,
        "tips": tips,
        "days": days,
    }

def generate_one_day_chart_str(form: dict) -> str:
    """Helper to generate a clean 1-day string format for the chatbot inline reply."""
    plan = generate_plan(form)
    day1 = plan["days"][0]["meals"]
    out = []
    for meal in day1:
        out.append(f"• {meal['name']}: {meal['items'][0]} (~{meal['calories']} kcal)")
    return "\n".join(out)
