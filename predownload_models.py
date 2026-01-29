from paddleocr import PaddleOCR

print("Downloading PaddleOCR models...")

ocr = PaddleOCR(
    lang="en",
    use_textline_orientation=True
)

print("PaddleOCR models downloaded successfully.")
