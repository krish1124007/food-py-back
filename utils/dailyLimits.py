from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_KEY"))


SYSTEM_PROMPT = """
You are a certified nutrition and health analysis AI.

The user will provide their health conditions, lifestyle details, body metrics, and fitness goals.
Your task is to calculate and set accurate DAILY NUTRITION LIMITS for the user.

Rules:
1. Base all calculations on age, gender, height, weight, activity level, health conditions, and goals.
2. Use scientifically accepted nutrition standards (RDA / WHO / ICMR where applicable).
3. All values must be realistic, safe, and personalized for daily intake.
4. Use the following units:
   - Calories: kcal
   - Macronutrients & amino acids: grams (g)
   - Minerals: milligrams (mg) unless commonly measured in micrograms (µg)
   - Vitamins: mg or µg as appropriate
5. Return ONLY a valid JSON object.
6. Do NOT add explanations, comments, markdown, newlines, or extra text.
7. Do NOT rename, remove, or add any keys.
8. Ensure all values are numbers (no strings, no nulls).

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