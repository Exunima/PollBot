import os
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from creation_survey.PDF_creator.pdf_handler import extract_text_from_pdf
from ner_model.deepseek_processor import process_text_with_deepseek
from database.tables.survey_data import Survey, SurveyQuestion, SurveyAnswerOption
from database.tables.test_data import Test, TestQuestion, TestAnswerOption

UPLOAD_FOLDER = "F:/BOT_TELEGRAM/PollBot/temp_files/pdf"

# Проверяем, существует ли папка
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


async def process_pdf_document(message: types.Message, state: FSMContext, bot: Bot):
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

    await message.answer("🔍 Отправляю текст в DeepSeek для анализа...")

    structured_data = process_text_with_deepseek(cleaned_text)

    if not structured_data:
        await message.answer("❌ DeepSeek вернул некорректные данные. Попробуйте снова.")
        return

    if "type" not in structured_data:
        await message.answer("❌ Ошибка: DeepSeek не определил, это тест или опрос.")
        return

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
                await TestAnswerOption.create(question=question, option_text=option["text"], is_correct=option["correct"])

        await message.answer("✅ Тест успешно сохранён в базе!")

    await message.answer("Вы можете начать прохождение теста или опроса!")

    await state.clear()


async def save_survey_to_db(data):
    """ Сохраняем тест в базу данных """
    survey = await Survey.create(survey_title=data["title"], survey_type="registered")

    for q in data["questions"]:
        question = await SurveyQuestion.create(survey=survey, question_text=q["question"], question_type="poll")

        for option in q["options"]:
            await SurveyAnswerOption.create(question=question, option_text=option)

    return survey
