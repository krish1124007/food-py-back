from paddleocr import PaddleOCR
import os
import uuid

# Global OCR instance (initially None)
_ocr_instance = None


def get_ocr():
    """
    Lazily initialize PaddleOCR only when first needed.
    This prevents Gunicorn startup timeout.
    """
    global _ocr_instance
    if _ocr_instance is None:
        print("Initializing PaddleOCR (lazy load)...")
        _ocr_instance = PaddleOCR(
            lang="en",
            use_textline_orientation=True
        )
    return _ocr_instance


def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text


def extract_text(image_input):
    """
    Extracts text from an image using PaddleOCR.
    Args:
        image_input: file path (str) OR file-like object (BytesIO/bytes)
    Returns:
        str: cleaned extracted text
    """
    temp_filename = None
    try:
        # Handle input
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                return ""
            target_path = image_input
        else:
            # Save bytes to temp file
            temp_filename = f"temp_ocr_{uuid.uuid4()}.jpg"
            with open(temp_filename, "wb") as f:
                if hasattr(image_input, "getvalue"):
                    f.write(image_input.getvalue())
                elif hasattr(image_input, "read"):
                    image_input.seek(0)
                    f.write(image_input.read())
                else:
                    f.write(image_input)

            target_path = temp_filename

        # 🔥 LAZY OCR INIT HERE
        ocr = get_ocr()

        # OCR prediction
        result = ocr.predict(target_path)

        texts = []
        for page in result:
            if "rec_texts" in page:
                texts.extend(page["rec_texts"])

        return clean_text("\n".join(texts))

    except Exception as e:
        print(f"OCR error: {e}")
        return ""

    finally:
        if temp_filename and os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except Exception:
                pass
