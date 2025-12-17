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
You are an expert nutrition-analysis AI.
Your task is to analyze the given inputs and return a SINGLE, valid JSON object.

INPUTS:
1. `user_today_details`: Foods eaten today, current macro/micronutrient intake.
2. `user_data`: User profile, health conditions, goals, daily limits.
3. `package_ingredients`: Extracted text from product, including ingredients and nutritional info.

OUTPUT FORMAT:
Return ONLY a single valid JSON object with the exact structure below. Do not include markdown formatting (like ```json), comments, or multiple JSON blocks.

JSON STRUCTURE:
{{
    "nutrient_summary": {{
        "calories": float,
        "protein": float,
        "carbs": float,
        "fat": float,
        "sugar": float,
        "fiber": float,
        "micronutrients": {{ ...flat list of vitamins and minerals... }}
    }},
    "ingredient_analysis": {{
        "healthy_ingredients": [str],
        "neutral_ingredients": [str],
        "harmful_ingredients": [str]
    }},
    "macro_nutrients": {{
        "calories": float,
        "protein": float,
        "carbs": float,
        "fat": float
    }},
    "micro_nutrients": {{ ...same as micronutrients in summary... }},
    "additives_and_preservatives": [str],
    "recommendation": "eat" | "avoid" | "eat_limited",
    "eat_or_not": boolean,
    "why_eat": str (reasoning if healthy),
    "why_avoid": str (reasoning if unhealthy),
    "health_condition_check": {{ ...dictionary of condition checks... }} or description string,
    "today_intake_comparison": {{ ...comparison data... }} or description string,
    "time_suitability": str (based on current time: {datetime.now().strftime("%H:%M")}),
    "better_alternative": [str] (list of better options if avoid)
}}

IMPORTANT RULES:
1. Return ONE single JSON object. Do not split into multiple objects.
2. Ensure all field names match exactly.
3. If specific numbers are missing, estimate based on standard food data or use 0.
4. "micro_nutrients" must be a flat object with keys like "vitaminA", "calcium", "iron", etc.
5. Analyze ingredients strictly (e.g., palm oil is harmful).
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



