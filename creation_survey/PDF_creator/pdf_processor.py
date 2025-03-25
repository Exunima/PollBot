import os
import json
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from creation_survey.PDF_creator.pdf_handler import extract_text_from_pdf
from ner_model.mistral_processor import process_text_with_mistral
from database.tables.survey_data import Survey, SurveyQuestion, SurveyAnswerOption
from database.tables.test_data import Test, TestQuestion, TestAnswerOption

UPLOAD_FOLDER = "F:/BOT_TELEGRAM/PollBot/temp_files/pdf"

# Проверяем, существует ли папка
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def clean_json_keys(json_data):
    """Удаляет лишние пробелы и скрытые символы из ключей JSON"""
    if isinstance(json_data, dict):
        return {k.strip(): clean_json_keys(v) for k, v in json_data.items()}
    elif isinstance(json_data, list):
        return [clean_json_keys(item) for item in json_data]
    return json_data


async def process_pdf_document(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка загруженного PDF-файла и передача в Mistral-7B"""

    pdf = message.document
    file_path = os.path.join(UPLOAD_FOLDER, pdf.file_name)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    file_info = await bot.get_file(pdf.file_id)
    await bot.download_file(file_info.file_path, destination=file_path)

    await message.answer("📄 Обрабатываю PDF...")

    extracted_text = extract_text_from_pdf(file_path)

    # 🔴 Убираем пустые строки и пробелы
    cleaned_text = "\n".join([line.strip() for line in extracted_text.split("\n") if line.strip()])

    if not cleaned_text:
        await message.answer("❌ Не удалось извлечь текст из PDF.")
        await state.clear()
        return

    await message.answer("🔍 Отправляю текст в Mistral-7B для анализа...")

    structured_data = process_text_with_mistral(cleaned_text)

    # ✅ Исправлено: Проверяем, является ли structured_data уже объектом JSON
    if isinstance(structured_data, str):
        try:
            structured_data = json.loads(structured_data)  # Конвертируем строку JSON в объект Python
        except json.JSONDecodeError:
            await message.answer("❌ Ошибка: JSON не разобран, ответ Mistral-7B некорректен.")
            return

    # ✅ Если JSON пришёл в списке `[{}]`, берём первый элемент
    if isinstance(structured_data, list) and len(structured_data) > 0:
        structured_data = structured_data[0]

    if not isinstance(structured_data, dict):
        await message.answer("❌ Ошибка: Mistral-7B вернула некорректный JSON (получен список, ожидался объект).")
        return

    # ✅ Очистка JSON перед обработкой
    structured_data = clean_json_keys(structured_data)

    if "type" not in structured_data:
        await message.answer("❌ Ошибка: Mistral-7B не определила, это тест или опрос.")
        return

    # Обрабатываем и сохраняем данные в БД
    if structured_data["type"] == "survey":
        survey = await Survey.create(survey_title=structured_data["title"], survey_type="registered")

        for q in structured_data["questions"]:
            question = await SurveyQuestion.create(survey=survey, question_text=q["text"], question_type="poll")

            for option in q["options"]:
                await SurveyAnswerOption.create(question=question, option_text=option)

        await message.answer("✅ Опрос успешно сохранён в базе!")

    elif structured_data["type"] == "test":
        test = await Test.create(title=structured_data["title"], duration_minutes=30, attempts=1)

        for q in structured_data["questions"]:
            question = await TestQuestion.create(test=test, question_text=q["text"])

            for option in q["options"]:
                await TestAnswerOption.create(question=question, option_text=option["text"],
                                              is_correct=option.get("correct", False))  # ✅ Исправлено!

        await message.answer("✅ Тест успешно сохранён в базе!")

    await message.answer("🎯 Вы можете начать прохождение теста или опроса!")

    await state.clear()


async def save_survey_to_db(data):
    """Сохраняем опрос в базу данных"""
    survey = await Survey.create(survey_title=data["title"], survey_type="registered")

    for q in data["questions"]:
        question = await SurveyQuestion.create(survey=survey, question_text=q["text"], question_type="poll")

        for option in q["options"]:
            await SurveyAnswerOption.create(question=question, option_text=option)

    return survey
