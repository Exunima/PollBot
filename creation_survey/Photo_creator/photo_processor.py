import os
import json
import pytesseract
import logging
from uuid import uuid4
from tempfile import NamedTemporaryFile
from PIL import Image
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from config.token_config import TESSERACT_PATH
from ner_model.mistral_processor import process_text_with_mistral
from creation_survey.PDF_creator.pdf_processor import clean_json_keys
from database.tables.users import User
from database.tables.survey_data import Survey, SurveyQuestion, SurveyAnswerOption, SurveyType, QuestionType
from database.tables.test_data import Test, TestQuestion, TestAnswerOption

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

TEMP_DIR = "F:/BOT_TELEGRAM/PollBot/temp_files/photo"
os.makedirs(TEMP_DIR, exist_ok=True)


def extract_text_from_photo(file_path: str) -> str:
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang="rus+eng")
        return text.strip()
    except Exception as e:
        logging.error(f"❌ Ошибка OCR: {e}")
        return ""


async def process_photo_document(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    document_type = data.get("document_type", "survey")
    duration_minutes = int(data.get("duration_minutes", 0))
    attempts = int(data.get("attempts", 1))
    duration_days = int(data.get("duration_days", 0))

    # Получаем файл от пользователя
    file_name = "photo.jpg"

    if message.photo:
        # Фото отправлено с камеры
        photo = message.photo[-1]
        file_id = photo.file_id
    elif message.document and message.document.mime_type.startswith("image/"):
        # Отправлено изображение как файл
        file_id = message.document.file_id
        file_name = message.document.file_name or "image.jpg"
    else:
        await message.answer("❌ Пожалуйста, отправьте изображение (фото или файл).")
        await state.clear()
        return

    # Скачиваем файл
    file_info = await bot.get_file(file_id)

    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[-1], dir=TEMP_DIR) as tmp:
        tmp_path = tmp.name
        await bot.download_file(file_info.file_path, tmp_path)

    local_path = tmp_path

    try:
        await message.answer("📸 Обрабатываю изображение...")
        extracted_text = extract_text_from_photo(local_path)
        logging.info(f"[OCR] Извлечённый текст:\n{extracted_text}")

        cleaned_text = "\n".join([line.strip() for line in extracted_text.split("\n") if line.strip()])

        if not cleaned_text:
            await message.answer("❌ Не удалось извлечь текст с изображения.")
            return

        await message.answer("🔍 Отправляю текст в Mistral-7B для анализа...")
        structured_data = process_text_with_mistral(cleaned_text, f"photo_{document_type}", filename=file_name)
        logging.info(f"[Mistral] Ответ модели:\n{structured_data}")

        if isinstance(structured_data, str):
            try:
                structured_data = json.loads(structured_data)
            except json.JSONDecodeError:
                await message.answer("❌ Ошибка: JSON не разобран, ответ Mistral-7B некорректен.")
                return

        if isinstance(structured_data, list) and structured_data:
            structured_data = structured_data[0]

        if not isinstance(structured_data, dict):
            await message.answer("❌ Ошибка: Mistral-7B вернула некорректный JSON (не dict).")
            return

        structured_data = clean_json_keys(structured_data)
        structured_data.setdefault("type", document_type)
        structured_data["title"] = structured_data.get("title") or "Из фото"
        questions_data = structured_data.get("questions", [])

        await message.answer(f"🔢 Вопросов найдено: {len(questions_data)}")

        user = await User.get_or_none(telegram_id=message.from_user.id)
        if not user:
            await message.answer("❌ Пользователь не найден в БД.")
            return

        access_key = str(uuid4())

        if structured_data["type"] == "survey":
            survey = await Survey.create(
                creator=user,
                survey_title=structured_data["title"],
                survey_type=SurveyType.REGISTERED,
                is_anonymous=False,
                access_key=access_key,
                attempts=1,
                duration_days=duration_days
            )

            saved_count = 0
            for q in questions_data:
                if not q.get("text") or not q.get("options"):
                    continue

                question = await SurveyQuestion.create(
                    survey=survey,
                    question_text=q["text"],
                    question_type=QuestionType.POLL
                )

                for option in q["options"]:
                    await SurveyAnswerOption.create(question=question, option_text=str(option).strip())

                saved_count += 1

            await message.answer(
                f"✅ Опрос «{survey.survey_title}» сохранён!\n"
                f"🔑 Ключ доступа: <code>{access_key}</code>\n"
                f"📌 Вопросов: {saved_count}",
                parse_mode="HTML"
            )

        elif structured_data["type"] == "test":
            test = await Test.create(
                creator=user,
                title=structured_data["title"],
                duration_minutes=duration_minutes,
                attempts=attempts,
                access_key=access_key
            )

            saved_count = 0
            for q in questions_data:
                if not q.get("text") or not q.get("options"):
                    continue

                if not any(opt.get("correct", False) for opt in q["options"] if isinstance(opt, dict)):
                    continue

                question = await TestQuestion.create(test=test, question_text=q["text"])

                for opt in q["options"]:
                    if isinstance(opt, dict) and "text" in opt:
                        option = await TestAnswerOption.create(question=question, option_text=opt["text"])
                        if opt.get("correct"):
                            await question.correct_answers.add(option)

                saved_count += 1

            await message.answer(
                f"✅ Тест «{test.title}» сохранён!\n"
                f"🔑 Ключ доступа: <code>{access_key}</code>\n"
                f"📌 Вопросов: {saved_count}",
                parse_mode="HTML"
            )

        else:
            await message.answer("❌ Ошибка: неизвестный тип документа. Ожидается 'test' или 'survey'.")

    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
        await state.clear()
