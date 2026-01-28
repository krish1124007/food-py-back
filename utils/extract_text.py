import pytesseract
from PIL import Image

def extract_text(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang="eng")
    return text.strip()

# import pytesseract
# from PIL import Image
# import os

# # Set the path to the tesseract.exe file from environment variable or use default
# tesseract_path = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
# pytesseract.pytesseract.tesseract_cmd = tesseract_path

# def extract_text(image_path):
#     try:
#         image = Image.open(image_path)
#         text = pytesseract.image_to_string(image, lang="eng")
#         return text.strip()
#     except Exception as e:
#         print(f"Error extracting text from image: {e}")
#         return ""  # Return empty string on error instead of crashing



