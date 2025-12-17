from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import requests
import io
import json
from utils.extract_text import extract_text
from utils.ai_answer import ai_answer
from utils.dailyLimits import setDailyLimits

app = FastAPI()

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

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    extracted_text = ""
    
    # Handle Image Text Extraction
    if request.product_Details.image_url:
        try:
            # Download the image
            response = requests.get(request.product_Details.image_url)
            response.raise_for_status()
            
            # extract_text expects a path or file-like object compatible with Image.open
            image_bytes = io.BytesIO(response.content)
            
            # Call the extraction function
            # note: extract_text.py uses Image.open(image_path), which works with BytesIO
            extracted_text = extract_text(image_bytes)
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            # We proceed even if image extraction fails, using available details
            pass

    # Prepare inputs for ai_answer
    # The requirement is to send the first two parameters "as it is" (converted to string for the function)
    # and construct the product details string with extracted text.
    
    user_today_details_str = json.dumps(request.dailyuserlimits)
    user_data_str = json.dumps(request.user_Details)
    
    package_ingredients_str = (
        f"Product Name: {request.product_Details.name}\n"
        f"Description: {request.product_Details.description}\n"
        f"Extracted Text from Image: {extracted_text}"
    )

    # Call AI Answer function
    ai_response_str = ai_answer(
        user_today_details_str,
        user_data_str,
        package_ingredients_str
    )
    print("THe answer of the response is " , ai_response_str)
    # Return the response
    # Attempt to parse as JSON if the AI returns a valid JSON string, otherwise return raw
    return ai_response_str


@app.post("/setDailyLimits")
async def set_daily_limits(request: SetDailyLimitsRequest):
    user_data = request.user_Details
    
    # Call setDailyLimits function
    result = setDailyLimits(user_data)
    
    # Return the result
    return result
