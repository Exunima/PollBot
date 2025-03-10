import pytesseract
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")


def extract_text_from_image(file_path):
    image = Image.open(file_path)
    return pytesseract.image_to_string(image, lang='rus')
