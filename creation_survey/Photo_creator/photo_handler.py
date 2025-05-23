import pytesseract
from PIL import Image, ImageFilter, ImageOps
import re

# Массовая таблица замены латинских букв
LATIN_TO_CYR = str.maketrans({
    "A": "А", "a": "а",
    "B": "В", "E": "Е", "e": "е",
    "K": "К", "M": "М",
    "H": "Н", "O": "О", "o": "о",
    "P": "Р", "C": "С", "c": "с",
    "T": "Т", "y": "у", "X": "Х",
    "x": "х", "Y": "У", "p": "р", "k": "к", "u": "и", "n": "п",
})

# Часто встречающиеся OCR-ошибки и артефакты
OCR_REPLACEMENTS = {
    "<)": "в)", "<©)": "в)", "bу": "бу", "сp": "–", "3,": "3.",
    "`": "'", "‘": "'", "’": "'", "“": '"', "”": '"',
    "Мup": "Мир", "Каk": "Как", "@)": "д)", "b)": "б)", "c)": "с)", "d)": "д)",
}


def preprocess_image_for_ocr(image: Image.Image, force_grayscale: bool = False) -> Image.Image:
    """
    Подготовка изображения для OCR.
    Если изображение уже черно-белое — можно пропустить серый режим.
    """
    if force_grayscale:
        gray = image.convert("L")
        contrast = ImageOps.autocontrast(gray)
        bw = contrast.point(lambda x: 0 if x < 180 else 255, "1")
        return bw.filter(ImageFilter.MedianFilter(size=3))
    else:
        return image.filter(ImageFilter.MedianFilter(size=1))


def fix_cyrillic_latin_mixing(text: str) -> str:
    """
    Замена символов латиницы, ошибочно распознанных в кириллических словах,
    и исправление частых OCR-ошибок.
    """
    for wrong, right in OCR_REPLACEMENTS.items():
        text = text.replace(wrong, right)

    text = text.translate(LATIN_TO_CYR)

    # Очистка пробелов, табов и лишнего мусора
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'[^\S\r\n]+', ' ', text)
    text = re.sub(r' +\n', '\n', text)

    return text


def extract_text_from_photo(file_path: str, force_grayscale: bool = False) -> str:
    """
    Основная функция распознавания текста с фото + постобработка.
    """
    try:
        original = Image.open(file_path)
        image = preprocess_image_for_ocr(original, force_grayscale=force_grayscale)
        raw_text = pytesseract.image_to_string(image, lang="rus+eng")
        fixed_text = fix_cyrillic_latin_mixing(raw_text.strip())
        return fixed_text
    except Exception as e:
        print(f"❌ Ошибка OCR: {e}")
        return ""
