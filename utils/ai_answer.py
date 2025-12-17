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
# SYSTEM PROMPT
# ==============================




# ==============================
# PYDANTIC MODELS
# ==============================

class IngredientAnalysis(BaseModel):
    healthy_ingredients: List[str] = []
    neutral_ingredients: List[str] = []
    harmful_ingredients: List[str] = []


class MacroNutrients(BaseModel):
    calories: Optional[float] = 0
    protein: Optional[float] = 0
    carbs: Optional[float] = 0
    fat: Optional[float] = 0
    sugar: Optional[float] = 0
    fiber: Optional[float] = 0


class MicroNutrients(BaseModel):
    # Vitamins
    vitaminA: float = 0
    vitaminB1: float = 0
    vitaminB2: float = 0
    vitaminB3: float = 0
    vitaminB5: float = 0
    vitaminB6: float = 0
    vitaminB7: float = 0
    vitaminB9: float = 0
    vitaminB12: float = 0
    vitaminC: float = 0
    vitaminD: float = 0
    vitaminE: float = 0
    vitaminK: float = 0

    # Minerals
    calcium: float = 0
    iron: float = 0
    magnesium: float = 0
    phosphorus: float = 0
    potassium: float = 0
    sodium: float = 0  # Moved from Macros
    zinc: float = 0
    copper: float = 0
    manganese: float = 0
    selenium: float = 0
    iodine: float = 0
    chromium: float = 0
    fluoride: float = 0
    molybdenum: float = 0

    # Fatty Acids
    omega3: float = 0
    omega6: float = 0

    # Amino Acids
    leucine: float = 0
    isoleucine: float = 0
    valine: float = 0
    lysine: float = 0
    methionine: float = 0
    phenylalanine: float = 0
    threonine: float = 0
    tryptophan: float = 0
    histidine: float = 0


class AiAnswer(BaseModel):
    nutrient_summary: Dict[str, float]
    ingredient_analysis: IngredientAnalysis
    macro_nutrients: MacroNutrients
    micro_nutrients: MicroNutrients
    additives_and_preservatives: List[str]

    recommendation: str  # "eat", "avoid", "eat_limited"
    eat_or_not:bool
    why_eat: Optional[str]
    why_avoid: Optional[str]
    health_condition_check: Optional[str]
    today_intake_comparison: Optional[str]

    time_suitability: Optional[str]
    better_alternative: Optional[str]



SYSTEM_PROMPT = f"""
You are an expert nutrition-analysis AI. You must ALWAYS return output in pure JSON format only — no explanations outside JSON.

You will receive three inputs:

1. `user_today_details`
   - Foods eaten today
   - Ingredients consumed
   - Calories, sugar, sodium, carbs, fat, protein consumed
   - Activities and calories burned

2. `user_data`
   - Age, height, weight, gender
   - Medical conditions (diabetes, BP, cholesterol, thyroid, PCOS, etc.)
   - Daily recommended nutrient limits based on their health profile
   - Diet goals (weight loss, gain, maintenance)

3. `package_ingredients`
   - Extracted ingredients from the scanned product
   - Macro nutrients (calories, protein, carbs, fats)
   - Micro nutrients (vitamins, minerals, sodium, sugar, fiber)
   - Additives, preservatives, artificial flavors, allergens
   - Anything harmful or beneficial

Your tasks:

A) Generate a complete structured JSON containing:
   - "nutrient_summary"
   - "ingredient_analysis":
        * "healthy_ingredients"
        * "neutral_ingredients"
        * "harmful_ingredients"
   - "macro_nutrients"
   - "micro_nutrients"
   - "additives_and_preservatives"

B) Generate a decision:
   - "recommendation": "eat", "avoid", or "eat_limited"

C) Provide detailed reasoning:
   -"eat_or_not"(boolean)
   - "why_eat"
   - "why_avoid"
   - "health_condition_check"
   - "today_intake_comparison"

D) Time-based recommendation:
   - Use current time: {datetime.now().strftime("%H:%M")}
   - "time_suitability"
   - "better_alternative"

E) If user doesn't provide any image and just provides the name of the food and some other details, then use that information.



F) NOTE: All ingredients check perefcely For example: palm oil is very dangerous for health so check it carefully There are many things are good for health but it's some clones are very dangerous for health like the any good quilty oil is very good for health but it's some clones are very dangerous for health like the palm oil is very dangerous for health.


Note : you main task is analysy package_ingredients and get the help og the user_data and user_today_details for the check the waht waht user today eat base on the you want to generate the full strucutre of the package_ingredients

OUTPUT RULES:
- Output MUST be strictly valid JSON.
- DO NOT output any text outside the JSON block.
- No explanations or commentary outside JSON.
- The structure of "micro_nutrients" must be a flat object with keys for all vitamins (vitaminA...), minerals (calcium...sodium...), fatty acids (omega3...), and amino acids.
"""


# ==============================
# GROQ LLM CALL FUNCTION
# ==============================

def ai_answer(
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
        model="llama-3.1-8b-instant"
    )

    raw = response.choices[0].message.content

    print(f"The Row answer is {raw}")

    # --- JSON Parsing ---
    return raw



