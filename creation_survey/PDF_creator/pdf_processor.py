import os
import json
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from creation_survey.PDF_creator.pdf_handler import extract_text_from_pdf
from ner_model.mistral_processor import process_text_with_mistral
from database.tables.survey_data import Survey, SurveyQuestion, SurveyAnswerOption, SurveyType, QuestionType
from database.tables.test_data import Test, TestQuestion, TestAnswerOption
from database.tables.users import User
from uuid import uuid4

UPLOAD_FOLDER = "F:/BOT_TELEGRAM/PollBot/temp_files/pdf"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def clean_json_keys(json_data):
    """Удаляет лишние пробелы и скрытые символы из ключей JSON"""
    if isinstance(json_data, dict):
        return {k.strip(): clean_json_keys(v) for k, v in json_data.items()}
    elif isinstance(json_data, list):
        return [clean_json_keys(item) for item in json_data]
    return json_data


async def process_pdf_document(message: types.Message, state: FSMContext, bot: Bot):
    pdf = message.document
    file_path = os.path.join(UPLOAD_FOLDER, pdf.file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    file_info = await bot.get_file(pdf.file_id)
    await bot.download_file(file_info.file_path, destination=file_path)

    await message.answer("📄 Обрабатываю PDF...")

    extracted_text = extract_text_from_pdf(file_path)
    cleaned_text = "\n".join([line.strip() for line in extracted_text.split("\n") if line.strip()])

    real_question_count = cleaned_text.lower().count("ответ:")

    if not cleaned_text:
        await message.answer("❌ Не удалось извлечь текст из PDF.")
        await state.clear()
        return

    await message.answer("🔍 Отправляю текст в Mistral-7B для анализа...")

    user_data = await state.get_data()
    prompt_type = user_data.get("document_type", "survey")
    structured_data = process_text_with_mistral(cleaned_text, prompt_type, filename=pdf.file_name)

    if "questions" in structured_data and isinstance(structured_data["questions"], list):
        # Удаляем обрезание:
        # structured_data["questions"] = structured_data["questions"][:real_question_count]

        print(f"🔢 Вопросов найдено в PDF по 'Ответ:': {real_question_count}")
        print(f"🔢 Вопросов передано в БД: {len(structured_data['questions'])}")

    if isinstance(structured_data, str):
        try:
            structured_data = json.loads(structured_data)
        except json.JSONDecodeError:
            await message.answer("❌ Ошибка: JSON не разобран, ответ Mistral-7B некорректен.")
            return

    if isinstance(structured_data, list) and len(structured_data) > 0:
        structured_data = structured_data[0]

    if not isinstance(structured_data, dict):
        await message.answer("❌ Ошибка: Mistral-7B вернула некорректный JSON.")
        return

    structured_data = clean_json_keys(structured_data)

    if "type" not in structured_data:
        await message.answer("❌ Ошибка: Mistral-7B не определила, это тест или опрос.")
        return

    user = await User.get_or_none(telegram_id=message.from_user.id)
    access_key = str(uuid4())

    if structured_data["type"] == "survey":
        survey = await Survey.create(
            creator=user,
            survey_title=structured_data["title"],
            survey_type=SurveyType.REGISTERED,
            is_anonymous=False,
            access_key=access_key,
            attempts=1,
            duration_days=0
        )

        for q in structured_data["questions"]:
            if not q.get("text") or not q.get("options"):
                continue

            question = await SurveyQuestion.create(
                survey=survey,
                question_text=q["text"],
                question_type=QuestionType.POLL
            )
            for option in q["options"]:
                await SurveyAnswerOption.create(question=question, option_text=option)

        await message.answer(
            f"✅ Опрос \"{structured_data['title']}\" сохранён!\n"
            f"🔑 Ключ доступа: <code>{access_key}</code>\n"
            f"📌 Отправьте его участникам.",
            parse_mode="HTML"
        )

    elif structured_data["type"] == "test":
        test = await Test.create(
            creator=user,
            title=structured_data["title"],
            duration_minutes=30,
            attempts=1,
            access_key=access_key
        )

        for q in structured_data["questions"]:
            # Валидация вопроса
            if not q.get("text") or not q.get("options"):
                continue

            correct_exists = any(opt.get("correct", False) for opt in q["options"])
            if not correct_exists:
                continue

            # Сохраняем только валидные вопросы
            question = await TestQuestion.create(test=test, question_text=q["text"])
            option_objs = []

            for option in q["options"]:
                opt = await TestAnswerOption.create(question=question, option_text=option["text"])
                option_objs.append((opt, option.get("correct", False)))

            for opt, is_correct in option_objs:
                if is_correct:
                    await question.correct_answers.add(opt)

        await message.answer(
            f"✅ Тест \"{structured_data['title']}\" сохранён!\n"
            f"🔑 Ключ доступа: <code>{access_key}</code>\n"
            f"📌 Передайте его участникам.",
            parse_mode="HTML"
        )

    await message.answer("🎯 Вы можете начать прохождение теста или опроса!")
    await state.clear()
