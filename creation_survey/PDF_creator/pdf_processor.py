import os
from aiogram import types
from aiogram.fsm.context import FSMContext
from creation_survey.PDF_creator.pdf_handler import extract_text_from_pdf
from ner_model.deepseek_processor import process_text_with_deepseek
from database.tables.survey_data import Survey, SurveyQuestion, SurveyAnswerOption

UPLOAD_FOLDER = "F:/BOT_TELEGRAM/PollBot/temp_files/pdf"


async def process_pdf_document(message: types.Message, state: FSMContext):
    """ Обрабатывает загруженный PDF-файл """
    pdf = message.document
    file_path = os.path.join(UPLOAD_FOLDER, pdf.file_name)

    # Сохраняем PDF-файл
    await pdf.download(destination=file_path)
    await message.answer("📄 Обрабатываю PDF...")

    # Извлекаем текст из PDF
    extracted_text = extract_text_from_pdf(file_path)

    if not extracted_text.strip():
        await message.answer("❌ Не удалось извлечь текст из PDF.")
        await state.clear()
        return

    await message.answer("🔍 Отправляю текст в DeepSeek для анализа...")

    # Передаём текст в DeepSeek
    structured_data = process_text_with_deepseek(extracted_text)

    # Проверяем, удалось ли получить JSON
    if not structured_data:
        await message.answer("⚠️ DeepSeek не смог корректно обработать тест.")
        return

    # Сохраняем тест в БД
    await save_survey_to_db(structured_data)

    # Отправляем пользователю тест на проверку
    await message.answer(f"✅ Вот, что получилось:\n\n{structured_data}")
    await message.answer("Проверь данные и подтверди, чтобы создать тест.")

    await state.clear()


async def save_survey_to_db(data):
    """ Сохраняем тест в базу данных """
    survey = await Survey.create(survey_title=data["title"], survey_type="registered")

    for q in data["questions"]:
        question = await SurveyQuestion.create(survey=survey, question_text=q["question"], question_type="poll")

        for option in q["options"]:
            await SurveyAnswerOption.create(question=question, option_text=option)

    return survey
