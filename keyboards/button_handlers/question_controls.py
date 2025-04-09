from aiogram import types
from aiogram.fsm.context import FSMContext
from database.tables.survey_data import Survey, SurveyQuestion, SurveyType, QuestionType, SurveyAnswerOption
from keyboards.button_creators.start_keyboard import create_start_keyboard
from database.tables.test_data import Test, TestQuestion, TestAnswerOption
from database.tables.users import User
from config.state_config import TestState
import uuid
from aiogram.utils.markdown import hbold, hcode


# Обработчик кнопки "Продолжить"
async def handle_continue(message: types.Message, state: FSMContext):
    """Обработчик кнопки 'Продолжить'"""
    await message.answer("Введите новый вопрос:")
    await state.set_state(TestState.waiting_for_question)


# Обработчик кнопки "Завершить"
async def handle_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    test_data = data.get("test_data", {})

    title = test_data.get("title")
    questions = test_data.get("questions", [])

    if not title or not questions:
        await message.answer("❌ Ошибка: у теста отсутствуют данные.")
        return

    access_key = str(uuid.uuid4())
    user = await User.get_or_none(telegram_id=message.from_user.id)

    test = await Test.create(
        creator=user,
        title=title,
        duration_minutes=test_data.get("duration_minutes", 30),
        attempts=test_data.get("attempts", 1),
        access_key=access_key
    )

    for question in questions:
        test_question = await TestQuestion.create(
            test=test,
            question_text=question["question_text"]
        )

        for answer_text in question.get("answers", []):
            await TestAnswerOption.create(
                question=test_question,
                option_text=answer_text
            )

        correct_answers_list = question.get("correct_answers", [])
        for answer_text in correct_answers_list:
            answer_option = await TestAnswerOption.get_or_none(
                option_text=answer_text,
                question=test_question
            )
            if answer_option:
                await test_question.correct_answers.add(answer_option)

    formatted_message = (
        f"🎉 Тест \"{title}\" создан!\n\n"
        f"🔑 Ваш уникальный ключ:\n{hcode(access_key)}\n\n"
        f"🕒 Время: {test.duration_minutes if test.duration_minutes else 'Неограниченно'} минут\n"
        f"🔄 Попытки: {test.attempts if test.attempts else 'Неограниченно'}"
    )

    await message.answer(
        formatted_message,
        parse_mode="HTML",
        reply_markup=create_start_keyboard()
    )

    await state.clear()
    return


# Обработчик кнопки "Выдать ключ" (для анонимного опроса)
async def handle_anonymous_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    survey_data = data.get("survey_data", {})

    title = survey_data.get("title")
    questions = survey_data.get("questions", [])

    if not title or not questions:
        await message.answer("❌ Ошибка: у опроса отсутствуют данные.")
        return

    access_key = str(uuid.uuid4())
    user = await User.get_or_none(telegram_id=message.from_user.id)

    survey = await Survey.create(
        creator=user,
        survey_title=title,
        survey_type=SurveyType.ANONYMOUS,
        is_anonymous=True,
        access_key=access_key,
        attempts=survey_data.get("attempts", 1),
        duration_days=survey_data.get("duration_days", 0)
    )

    for question in questions:
        created_question = await SurveyQuestion.create(
            survey=survey,
            question_text=question["question_text"],
            question_type=QuestionType.POLL
        )
        for option_text in question.get("options", []):
            await SurveyAnswerOption.create(
                question=created_question,
                option_text=option_text
            )

    formatted_message = (
        f"🎉 Анонимный опрос \"{title}\" создан!\n\n"
        f"🔑 Ваш ключ:\n{hcode(access_key)}\n\n"
        f"{hbold('Скопируйте этот ключ для распространения')}"
    )

    await message.answer(
        formatted_message,
        parse_mode="HTML",
        reply_markup=create_start_keyboard()
    )

    await state.clear()
    return
