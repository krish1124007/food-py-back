from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import requests
import io
import json
import os

from utils.extract_text import extract_text
from utils.nutrition_analytics_agent import nutrition_analytics_agent
from utils.dailyLimits import setDailyLimits

app = FastAPI()


# ---------- MODELS ----------

class ProductDetails(BaseModel):
    image_url: Optional[str] = None
    name: str
    description: str


class AnalyzeRequest(BaseModel):
    dailyuserlimits: Dict[str, Any]
    user_Details: Dict[str, Any]
    product_Details: ProductDetails


class SetDailyLimitsRequest(BaseModel):
    user_Details: Dict[str, Any]


# ---------- ROUTES ----------

@app.get("/")
def health_check():
    return {"status": "OK"}


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        extracted_text = ""

        # ----- IMAGE TEXT EXTRACTION -----
        if request.product_Details.image_url:
            try:
                response = requests.get(
                    request.product_Details.image_url,
                    timeout=10
                )
                response.raise_for_status()

                image_bytes = io.BytesIO(response.content)
                extracted_text = extract_text(image_bytes)

            except Exception as e:
                print("Image extraction failed:", e)

        # ----- PREPARE DATA -----
        user_today_details_str = json.dumps(request.dailyuserlimits)
        user_data_str = json.dumps(request.user_Details)

        package_ingredients_str = (
            f"Product Name: {request.product_Details.name}\n"
            f"Description: {request.product_Details.description}\n"
            f"Extracted Text: {extracted_text}"
        )

        # ----- AI CALL -----
        ai_response = nutrition_analytics_agent(
            user_today_details_str,
            user_data_str,
            package_ingredients_str
        )

        print("The answer is :" , ai_response)
        # ----- ALWAYS RETURN JSON -----
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "ai_response": ai_response
            }
        )

    except Exception as e:
        print("Analyze error:", e)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal AI processing failed"
            }
        )


@app.post("/setDailyLimits")
async def set_daily_limits(request: SetDailyLimitsRequest):
    try:
        result = setDailyLimits(request.user_Details)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        print("Daily limits error:", e)
        raise HTTPException(status_code=500, detail="Failed to set daily limits")
