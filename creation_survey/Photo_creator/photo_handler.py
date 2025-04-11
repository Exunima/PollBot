import pytesseract
from PIL import Image, ImageFilter, ImageOps


def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    gray = image.convert("L")
    contrast = ImageOps.autocontrast(gray)
    bw = contrast.point(lambda x: 0 if x < 160 else 255, "1")
    return bw.filter(ImageFilter.MedianFilter(size=3))


def fix_cyrillic_latin_mixing(text: str) -> str:
    replacements = {
        "A": "А", "a": "а",
        "B": "В", "E": "Е", "e": "е",
        "K": "К", "M": "М",
        "H": "Н", "O": "О", "o": "о",
        "P": "Р", "C": "С", "c": "с",
        "T": "Т", "y": "у", "X": "Х"
    }
    return ''.join(replacements.get(ch, ch) for ch in text)


def extract_text_from_photo(file_path: str) -> str:
    try:
        original = Image.open(file_path)
        image = preprocess_image_for_ocr(original)
        text = pytesseract.image_to_string(image, lang="rus+eng")
        fixed_text = fix_cyrillic_latin_mixing(text.strip())
        return fixed_text
    except Exception as e:
        print(f"❌ Ошибка OCR: {e}")
        return ""
