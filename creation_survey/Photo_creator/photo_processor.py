import os
import logging
from uuid import uuid4
from tempfile import NamedTemporaryFile
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from config.token_config import TESSERACT_PATH
from config.state_config import ConfirmOCRState
from ner_model.mistral_processor import process_text_with_mistral, clean_json_keys
from database.tables.users import User
from database.tables.survey_data import Survey, SurveyQuestion, SurveyAnswerOption, SurveyType, QuestionType
from database.tables.test_data import Test, TestQuestion, TestAnswerOption
from creation_survey.Photo_creator.photo_handler import extract_text_from_photo
from keyboards.button_creators.confirm_ocr_keyboard import confirm_ocr_keyboard

import pytesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

TEMP_DIR = "F:/BOT_TELEGRAM/PollBot/temp_files/photo"
os.makedirs(TEMP_DIR, exist_ok=True)


async def process_photo_document(message: types.Message, state: FSMContext, bot: Bot):
    """Основная точка входа после загрузки фото"""
    data = await state.get_data()
    document_type = data.get("document_type", "survey")

    file_name = "photo.jpg"

    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document and message.document.mime_type.startswith("image/"):
        file_id = message.document.file_id
        file_name = message.document.file_name or "image.jpg"
    else:
        await message.answer("❌ Пожалуйста, отправьте изображение (фото или файл).")
        await state.clear()
        return

    file_info = await bot.get_file(file_id)
    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[-1], dir=TEMP_DIR) as tmp:
        tmp_path = tmp.name
        await bot.download_file(file_info.file_path, tmp_path)

    try:
        await message.answer("📸 Обрабатываю изображение...")
        extracted_text = extract_text_from_photo(tmp_path)
        logging.info(f"[OCR] Извлечённый текст:\n{extracted_text}")

        cleaned_text = "\n".join([line.strip() for line in extracted_text.split("\n") if line.strip()])

        if not cleaned_text:
            await message.answer("❌ Не удалось извлечь текст с изображения.")
            await state.clear()
            return

        await state.update_data(extracted_text=cleaned_text)
        await message.answer(
            f"📋 Вот что получилось после распознавания текста:\n\n{cleaned_text[:3000]}",
            reply_markup=confirm_ocr_keyboard()
        )
        await state.set_state(ConfirmOCRState.waiting_for_choice)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


async def process_clean_text_after_ocr(message: types.Message, state: FSMContext, bot: Bot, cleaned_text: str):
    """Обработка текста после подтверждения или редактирования пользователем"""
    data = await state.get_data()
    document_type = data.get("document_type", "survey")
    duration_minutes = int(data.get("duration_minutes", 0))
    attempts = int(data.get("attempts", 1))
    duration_days = int(data.get("duration_days", 0))
    filename = "photo.jpg"

    await message.answer("🔍 Отправляю текст в Mistral-7B для анализа...")
    structured_data = process_text_with_mistral(cleaned_text, f"photo_{document_type}", filename)
    logging.info(f"[Mistral] Ответ модели:\n{structured_data}")

    # Парсинг JSON
    import json
    if isinstance(structured_data, str):
        try:
            structured_data = json.loads(structured_data)
        except json.JSONDecodeError:
            await message.answer("❌ JSON от модели не разобран.")
            await state.clear()
            return

    if isinstance(structured_data, list) and structured_data:
        structured_data = structured_data[0]

    if not isinstance(structured_data, dict):
        await message.answer("❌ Некорректный формат ответа от модели.")
        await state.clear()
        return

    structured_data = clean_json_keys(structured_data)
    structured_data.setdefault("type", document_type)
    structured_data["title"] = structured_data.get("title") or "Из фото"
    questions_data = structured_data.get("questions", [])

    if not questions_data:
        await message.answer("⚠️ Не удалось найти ни одного вопроса. Проверьте текст.")
        await state.clear()
        return

    await message.answer(f"🔢 Вопросов найдено: {len(questions_data)}")

    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user:
        await message.answer("❌ Пользователь не найден в БД.")
        await state.clear()
        return

    access_key = str(uuid4())

    if structured_data["type"] == "test":
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
            f"✅ Тест «{test.title}» сохранён!\n🔑 Ключ доступа: <code>{access_key}</code>\n📌 Вопросов: {saved_count}",
            parse_mode="HTML"
        )

    elif structured_data["type"] == "survey":
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

    else:
        await message.answer("❌ Ошибка: неизвестный тип документа.")

    await state.clear()
