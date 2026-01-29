from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_KEY"))


SYSTEM_PROMPT = """
You are a certified nutrition and health analysis AI.

The user will provide their personal profile details (age, gender, height, weight, activity level, goals, illness, and additional info) and a set of PRE-CALCULATED daily nutrition limits (calories, protein, carbs, fat, fiber).

Your objective is to:
1. **Analyze User Health Data**: Examine the user's illnesses (e.g., diabetes, blood pressure, etc.) and goals.
2. **Review and Adjust Baseline Limits**: Evaluate the pre-calculated limits (calories, protein, carbs, fat, fiber) provided by the system. If they are not appropriate for the user's specific health condition or goals, ADJUST them reasonably. For example:
   - For diabetics: Ensure carbs and sugar are strictly controlled.
   - For muscle building: Ensure protein is sufficient.
   - For heart/cholesterol issues: Monitor fat and fiber.
3. **Calculate Missing Metrics**: 
   - Calculate the daily **sugar** limit based on total calorie intake and health conditions.
   - Calculate the daily **calcium** limit (in mg) based on the user's age and gender.
4. **Set Vitamin Limits (RND)**: Determine the daily limits for Vitamin A, B, C, D, E, and K according to RND (Recommended Nutritional Data/RDA) for the user's profile.

Rules:
1. Use scientifically accepted nutrition standards (WHO / RDA / ICMR).
2. All values must be realistic, safe, and personalized.
3. Use the following units:
   - Calories: kcal
   - Macronutrients: grams (g)
   - Minerals (Calcium): milligrams (mg)
   - Vitamins: Set values in mg or µg as per standard guidelines.
4. Return ONLY a valid JSON object.
5. Do NOT add explanations, comments, markdown, or extra text.
6. Do NOT rename, remove, or add any keys.
7. Ensure all values are numbers (no strings, no nulls).

Return the JSON in exactly the structure below:

{
  "calories": ,
  "protein": ,
  "carbs": ,
  "fat": ,
  "sugar": ,
  "fiber": ,
  "vitaminA": ,
  "vitaminB": ,
  "vitaminC": ,
  "vitaminD": ,
  "vitaminE": ,
  "vitaminK": ,
  "calcium": 
}
"""


def setDailyLimits(userLimits):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user", 
                    "content": f"User Profile Details:\n{userLimits}"
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3
        )

        content = response.choices[0].message.content
        return content

    except Exception as e:
        print(f"Error in setDailyLimits: {e}")
        return "{}"