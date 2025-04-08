import os
import json
import logging
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

    # 1) Скачиваем PDF
    file_info = await bot.get_file(pdf.file_id)
    await bot.download_file(file_info.file_path, destination=file_path)
    logging.info(f"Файл PDF сохранён в: {file_path}")

    await message.answer("📄 Обрабатываю PDF...")

    # 2) Извлекаем текст
    extracted_text = extract_text_from_pdf(file_path)
    cleaned_text = "\n".join([line.strip() for line in extracted_text.split("\n") if line.strip()])
    logging.info(f"Извлечённый текст:\n{cleaned_text}")

    if not cleaned_text:
        await message.answer("❌ Не удалось извлечь текст из PDF.")

        # Удаляем PDF-файл после завершения
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"PDF удалён после обработки: {file_path}")

        await state.clear()
        return

    await message.answer("🔍 Отправляю текст в Mistral-7B для анализа...")

    # 3) Узнаём, что выбрал пользователь (test/survey)
    user_data = await state.get_data()

    duration_minutes = int(user_data.get("duration_minutes", 0))
    attempts = int(user_data.get("attempts", 1))
    duration_days = int(user_data.get("duration_days", 0))
    document_type = user_data.get("document_type", "test")

    prompt_type = user_data.get("document_type", "survey")  # по умолчанию survey
    logging.info(f"document_type (prompt_type) = {prompt_type}")

    # 4) Обрабатываем текст моделью
    structured_data = process_text_with_mistral(cleaned_text, prompt_type, filename=pdf.file_name)
    logging.info(f"Ответ Mistral (structured_data): {structured_data}")

    # 5) Если строка - пробуем JSON-декод
    if isinstance(structured_data, str):
        try:
            structured_data = json.loads(structured_data)
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError: {e}")
            await message.answer("❌ Ошибка: JSON не разобран, ответ Mistral-7B некорректен.")
            return

    # Если список - берём первый элемент
    if isinstance(structured_data, list) and len(structured_data) > 0:
        structured_data = structured_data[0]

    # Проверяем тип (dict)
    if not isinstance(structured_data, dict):
        logging.warning("structured_data не является dict! Прерываем.")
        await message.answer("❌ Ошибка: Mistral-7B вернула некорректный JSON (не dict).")
        return

    structured_data = clean_json_keys(structured_data)

    # 6) Проверяем поле type, если нет - ошибка
    if "type" not in structured_data:
        logging.warning("В structured_data нет поля 'type'!")
        await message.answer("❌ Ошибка: Mistral-7B не указала 'type' (test или survey).")
        return

    # 7) Если модель не вернула title, или он пуст - берём имя файла
    doc_name = pdf.file_name.rsplit(".", 1)[0]
    title_in_json = structured_data.get("title", "").strip() or doc_name
    structured_data["title"] = title_in_json

    # 8) Сколько вопросов
    questions_data = structured_data.get("questions", [])
    found_questions = len(questions_data)
    logging.info(f"Количество вопросов в JSON: {found_questions}")
    await message.answer(f"🔢 Всего вопросов в JSON от модели: {found_questions}")

    # 9) Ищем пользователя
    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user:
        logging.warning(f"Пользователь с telegram_id={message.from_user.id} не найден в БД.")
        await message.answer("❌ Пользователь не найден в БД.")

        # Удаляем PDF-файл после завершения
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"PDF удалён после обработки: {file_path}")

        await state.clear()
        return

    # 10) Создаём ключ
    access_key = str(uuid4())
    logging.info(f"Будет создан ключ: {access_key}")

    # 11) Создаём либо тест, либо опрос
    if structured_data["type"] == "survey":
        survey = await Survey.create(
            creator=user,
            survey_title=title_in_json,
            survey_type=SurveyType.REGISTERED,
            is_anonymous=False,
            access_key=access_key,
            attempts=1,
            duration_days=duration_days
        )

        logging.info(f"Создан Survey c ID={survey.id}, title={survey.survey_title}")

        saved_count = 0
        for i, q in enumerate(questions_data, start=1):
            # Логируем каждый вопрос
            logging.info(f"[SURVEY] Обработка вопроса #{i}: {q}")

            text_val = q.get("text", "").strip()
            options_val = q.get("options")
            if not text_val or not options_val:
                logging.warning(f"[SURVEY] Пропущен вопрос #{i}, т.к. text или options пустые. text='{text_val}', options='{options_val}'")
                continue

            question = await SurveyQuestion.create(
                survey=survey,
                question_text=text_val,
                question_type=QuestionType.POLL
            )
            logging.info(f"[SURVEY] question_id={question.id}, question_text='{text_val}'")

            for opt_idx, option_text in enumerate(options_val, start=1):
                opt_str = str(option_text).strip()  # На случай если это не str
                if not opt_str:
                    logging.warning(f"[SURVEY] Пустой вариант ответа, пропускаем. opt_idx={opt_idx}")
                    continue
                created_opt = await SurveyAnswerOption.create(
                    question=question,
                    option_text=opt_str
                )
                logging.info(f"[SURVEY] answer_option_id={created_opt.id}, text='{opt_str}'")

            saved_count += 1

        await message.answer(
            f"✅ Опрос «{survey.survey_title}» сохранён!\n"
            f"📅 Дней на прохождение: {duration_days if duration_days else 'без ограничений'}\n"
            f"🔑 Ключ доступа: <code>{access_key}</code>\n"
            f"📌 Вопросов добавлено: {saved_count}",
            parse_mode="HTML"
        )

    elif structured_data["type"] == "test":
        test = await Test.create(
            creator=user,
            title=title_in_json,
            duration_minutes=duration_minutes,
            attempts=attempts,
            access_key=access_key
        )
        logging.info(f"Создан Test c ID={test.id}, title={test.title}")

        saved_count = 0
        for i, q in enumerate(questions_data, start=1):
            logging.info(f"[TEST] Обработка вопроса #{i}: {q}")

            text_val = q.get("text", "").strip()
            options_val = q.get("options")
            if not text_val or not options_val:
                logging.warning(f"[TEST] Пропущен вопрос #{i}, т.к. text или options пустые. text='{text_val}', options='{options_val}'")
                continue

            if not any(opt.get("correct", False) for opt in options_val if isinstance(opt, dict)):
                logging.warning(f"[TEST] Пропущен вопрос #{i}, нет правильных ответов (correct=true)")
                continue

            question = await TestQuestion.create(
                test=test,
                question_text=text_val
            )
            logging.info(f"[TEST] Создан вопрос ID={question.id}, text='{text_val}'")

            option_objs = []
            for opt_idx, opt_dict in enumerate(options_val, start=1):
                # opt_dict предполагается вида {"text": "...", "correct": bool}
                if not isinstance(opt_dict, dict):
                    logging.warning(f"[TEST] Вопрос #{i}, вариант #{opt_idx} - не dict! Пропускаем. opt_dict={opt_dict}")
                    continue

                opt_text = opt_dict.get("text", "").strip()
                if not opt_text:
                    logging.warning(f"[TEST] Вопрос #{i}, вариант #{opt_idx} - text пустой! Пропускаем.")
                    continue

                created_opt = await TestAnswerOption.create(
                    question=question,
                    option_text=opt_text
                )
                is_correct = bool(opt_dict.get("correct", False))
                logging.info(f"[TEST] answer_option_id={created_opt.id}, text='{opt_text}', correct={is_correct}")
                option_objs.append((created_opt, is_correct))

            # Добавляем correct
            for (opt_item, is_correct) in option_objs:
                if is_correct:
                    await question.correct_answers.add(opt_item)

            saved_count += 1

        await message.answer(
            f"✅ Тест «{test.title}» сохранён!\n"
            f"⏱️ Время на прохождение: {duration_minutes} мин.\n"
            f"🔁 Попыток: {'неограниченно' if attempts == 0 else attempts}\n"
            f"🔑 Ключ доступа: <code>{access_key}</code>\n"
            f"📌 Вопросов добавлено: {saved_count}",
            parse_mode="HTML"
        )

    else:
        logging.warning(f"Неизвестный тип документа: {structured_data['type']}")
        await message.answer("❌ Ошибка: неизвестный тип документа. Ожидается 'survey' или 'test'.")

    # Завершение
    await message.answer("🎯 Можете начать прохождение теста или опроса!")

    # Удаляем PDF-файл после завершения
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"PDF удалён после обработки: {file_path}")

    await state.clear()
    logging.info("process_pdf_document завершён успешно.")
