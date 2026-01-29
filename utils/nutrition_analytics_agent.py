from groq import Groq
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import json
from dotenv import load_dotenv
import os

load_dotenv()
# Load environment variables from .env file

client = Groq(api_key=os.getenv("GROQ_KEY"))

# ==============================
# PYDANTIC MODELS
# ==============================

class IngredientAnalysis(BaseModel):
    healthy_ingredients: List[str] = []
    neutral_ingredients: List[str] = []
    harmful_ingredients: List[str] = []


class DbUpdateIngredients(BaseModel):
    calories: Optional[float] = 0
    protein: Optional[float] = 0
    carbs: Optional[float] = 0
    fat: Optional[float] = 0
    sugar: Optional[float] = 0
    fiber: Optional[float] = 0
    vitaminA: float = 0
    vitaminB: float = 0
    vitaminC: float = 0
    vitaminD: float = 0
    vitaminE: float = 0
    vitaminK: float = 0
    calcium: float = 0
    


class AiAnswer(BaseModel):
    ingredient_analysis: IngredientAnalysis
    DbUpdateIngredients: DbUpdateIngredients
    additives_and_preservatives: List[str]

    recommendation: str  # "eat", "avoid", "eat_limited"
    eat_or_not:bool
    why_eat: Optional[str]
    why_avoid: Optional[str]
    health_condition_check: Optional[str]
    today_intake_comparison: Optional[str]

    time_suitability: Optional[str]
    better_alternative: Optional[List[str]] = []  # Changed to List[str]




SYSTEM_PROMPT = f"""
You are an expert nutrition-analysis AI with deep knowledge of food labels, ingredients, and nutritional science.
Your task is to analyze the given inputs and return a SINGLE, valid JSON object.

INPUTS:
1. `user_today_details`: Foods eaten today, current macro/micronutrient intake.
2. `user_data`: User profile, health conditions, goals, daily limits, user additional info.
3. `package_ingredients`: Extracted text from product label, including ingredients list and nutritional information table.

🔴 CRITICAL INSTRUCTIONS FOR LABEL READING:
1. **STRICTLY READ THE NUTRITION LABEL**: If a nutrition facts table is present in the extracted text, use EXACTLY those values. Do NOT estimate or guess when label data is available.
2. **INGREDIENTS LIST PRIORITY**: Carefully read the complete ingredients list. Ingredients are listed in order of quantity (highest to lowest).
3. **HARMFUL INGREDIENTS TO FLAG**: palm oil, hydrogenated oils, trans fats, high fructose corn syrup, artificial colors (Red 40, Yellow 5, Yellow 6, Blue 1, etc.), sodium benzoate, BHA, BHT, MSG, artificial sweeteners in excess (aspartame, sucralose, acesulfame K), excessive sodium (>400mg per serving).
4. **SERVING SIZE ATTENTION**: Pay close attention to serving size. If label shows "per 100g" or "per serving (50g)", calculate accordingly for the actual amount.
5. **LABEL ACCURACY IS MANDATORY**: If nutritional values are clearly stated on the label, use them EXACTLY as written. Only estimate vitamins/minerals if not provided on label.

OUTPUT FORMAT:
Return ONLY a single valid JSON object with the exact structure below. Do not include markdown formatting (like ```json), comments, or multiple JSON blocks.

JSON STRUCTURE:
{{
    "DbUpdateIngredients": {{
        "calories": float,      # MUST read from label if available (kcal)
        "protein": float,       # MUST read from label if available (grams)
        "carbs": float,         # MUST read from label if available (grams) - total carbohydrates
        "fat": float,           # MUST read from label if available (grams) - total fat
        "sugar": float,         # MUST read from label if available (grams)
        "fiber": float,         # MUST read from label if available (grams) - dietary fiber
        "vitaminA": float,      # In mcg RAE or IU, read from label or estimate based on ingredients
        "vitaminB": float,      # Combined B vitamins in mg (B1+B2+B3+B6+B12)
        "vitaminC": float,      # In mg, read from label or estimate
        "vitaminD": float,      # In mcg or IU, read from label or estimate
        "vitaminE": float,      # In mg, read from label or estimate
        "vitaminK": float,      # In mcg, read from label or estimate
        "calcium": float        # In mg, read from label or estimate
    }},
    "ingredient_analysis": {{
        "healthy_ingredients": [str],    # List all beneficial ingredients found (whole grains, fruits, vegetables, nuts, etc.)
        "neutral_ingredients": [str],    # List neutral ingredients (water, salt in moderation, common additives)
        "harmful_ingredients": [str]     # List ALL harmful ingredients found (be strict and thorough!)
    }},
    "additives_and_preservatives": [str],  # List all E-numbers, preservatives, artificial additives, stabilizers
    "recommendation": "eat" | "avoid" | "eat_limited",  # eat=healthy, avoid=unhealthy, eat_limited=okay in moderation
    "eat_or_not": boolean,  # true if recommendation is "eat", false if "avoid" or "eat_limited"
    "why_eat": str (detailed reasoning if healthy/eat_limited, null if avoid),
    "why_avoid": str (detailed reasoning if avoid, null if eat/eat_limited),
    "health_condition_check": str (analyze against user's illnesses: diabetes→check sugar/carbs, hypertension→check sodium, heart disease→check saturated fat, allergies→check allergens),
    "today_intake_comparison": str (compare with what user has eaten today and their daily limits - are they close to limits?),
    "time_suitability": str (based on current time: {datetime.now().strftime("%H:%M")} - is this food suitable? Heavy meals not good late night, sugary items not good morning empty stomach, etc.),
    "better_alternative": [str] (if recommending avoid/eat_limited, provide 2-3 specific healthier alternatives that serve similar purpose)
}}

🔴 MANDATORY RULES:
1. **LABEL ACCURACY**: If nutrition facts table exists in extracted text, use those EXACT values for calories, protein, carbs, fat, sugar, fiber. Do NOT estimate these if label provides them.
2. **INGREDIENT THOROUGHNESS**: Read the COMPLETE ingredients list. Identify ALL harmful ingredients, not just obvious ones.
3. **SERVING SIZE CALCULATION**: If label shows "per 100g" but typical serving is 50g, use the 100g values (user will adjust).
4. **HEALTH CONDITIONS**: Cross-check ingredients against user's specific health conditions and illnesses.
5. **DAILY LIMITS COMPARISON**: Compare nutritional values with user's daily limits and today's intake.
6. **TIME AWARENESS**: Consider current time ({datetime.now().strftime("%H:%M")}) for meal suitability.
7. **ALTERNATIVES REQUIRED**: If recommendation is "avoid" or "eat_limited", MUST provide 2-3 specific better alternatives.
8. **NO GUESSING MACROS**: Only estimate vitamins/minerals. For calories, protein, carbs, fat, sugar, fiber - ALWAYS use label if present, otherwise use standard food database values.
9. **STRICT HARMFUL DETECTION**: Be strict about harmful ingredients. If palm oil, trans fats, or artificial colors are present, flag them.

EXAMPLE LABEL READING:
If extracted text contains: "Nutrition Facts: Calories 250, Protein 8g, Total Carbohydrate 35g, Total Fat 9g, Sugars 12g, Dietary Fiber 2g"
Then DbUpdateIngredients MUST have: calories: 250, protein: 8, carbs: 35, fat: 9, sugar: 12, fiber: 2

Return ONE single JSON object. Ensure all field names match exactly. Be thorough and accurate.
"""


# ==============================
# GROQ LLM CALL FUNCTION
# ==============================

def nutrition_analytics_agent(
    user_today_details: str,
    user_data: str,
    package_ingredients: str
) -> AiAnswer:

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content":
                    f"user_today_details: {user_today_details}\n"
                    f"user_data: {user_data}\n"
                    f"package_ingredients: {package_ingredients}"
            }
        ],
        model="llama-3.1-8b-instant",
        temperature=0.3  # Lower temperature for more consistent, accurate results
    )

    raw = response.choices[0].message.content

    print(f"The Raw answer is: {raw}")

    # --- JSON Parsing / Cleaning ---
    # Remove markdown code blocks if present
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    return cleaned.strip()



