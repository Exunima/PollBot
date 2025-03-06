import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
TESSERACT_PATH = os.getenv("TESSERACT_PATH")
