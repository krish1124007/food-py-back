import pytesseract
from PIL import Image

def extract_text(image_path):
    # 1. Set Tesseract executable path (Windows only)
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # 2. Load the image
    image = Image.open(image_path)

    # 3. Extract text
    text = pytesseract.image_to_string(image, lang="eng")

    return text.strip()


