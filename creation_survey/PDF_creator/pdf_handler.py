from pypdf import PdfReader


def extract_text_from_pdf(file_path):
    """ Извлекает текст из PDF с помощью библиотеки pypdf """
    text = []
    try:
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text.append(page.extract_text())  # Извлекаем текст со всех страниц
    except Exception as e:
        print(f"Ошибка при извлечении текста из PDF: {e}")
        return ""

    return "\n".join(text).strip()  # Собираем текст в строку
