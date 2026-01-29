from paddleocr import PaddleOCR
import os
import tempfile
import uuid

# Initialize global OCR instance to avoid reloading model on every request
# Using the configuration provided by the user
ocr = PaddleOCR(
    lang='en',
    use_textline_orientation=True
)

def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text

def extract_text(image_input):
    """
    Extracts text from an image using PaddleOCR.
    Args:
        image_input: Can be a file path (str) or a file-like object (BytesIO)
    Returns:
        str: The cleaned extracted text
    """
    temp_filename = None
    try:
        # Handle input: determine if it's a path or bytes
        if isinstance(image_input, str):
             if not os.path.exists(image_input):
                 return ""
             target_path = image_input
        else:
            # Assume it is bytes/BytesIO, save to a temp file
            # Create a unique temp file
            temp_filename = f"temp_ocr_{uuid.uuid4()}.jpg"
            with open(temp_filename, "wb") as f:
                if hasattr(image_input, 'getvalue'):
                    f.write(image_input.getvalue())
                elif hasattr(image_input, 'read'):
                    image_input.seek(0)
                    f.write(image_input.read())
                else:
                    # Try writing directly if it's bytes
                    f.write(image_input)
            target_path = temp_filename

        # Run OCR prediction
        # Using the exact snippet logic provided by the user
        result = ocr.predict(target_path)
        
        texts = []
        # OCRv5 result structure parsing
        # result is likely a generator or list
        for page in result:
            if "rec_texts" in page:
                texts.extend(page["rec_texts"])

        final_text = "\n".join(texts)
        
        # Apply cleaning
        return clean_text(final_text)

    except Exception as e:
        print(f"Error in extract_text: {e}")
        return ""
    finally:
        # Cleanup temp file if created
        if temp_filename and os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except:
                pass
