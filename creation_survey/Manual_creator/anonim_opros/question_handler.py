from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import AnonymousSurveyState
from creation_survey.Manual_creator.validate_input import (
    is_valid_question,
    validate_options
)

from keyboards.button_creators.anonymous_survey_keyboard import anonymous_survey_keyboard

router = Router()


@router.message(AnonymousSurveyState.waiting_for_question)
async def get_question_text(message: types.Message, state: FSMContext):
    """
    Получаем текст вопроса, проверяем его валидность и добавляем в опрос.
    """
    question_text = message.text.strip()

    data = await state.get_data()
    survey_data = data.get("survey_data", {})
    existing_questions = [q["question_text"] for q in survey_data.get("questions", [])]

    if not is_valid_question(question_text, existing_questions):
        await message.answer(" Вопрос должен содержать не менее 5 символов и не повторяться.")
        return

    survey_data["questions"].append({"question_text": question_text, "options": []})
    await state.update_data(survey_data=survey_data)

    await message.answer("Введите варианты ответа, разделяя их `;` (пример: Да; Нет; Возможно)")
    await state.set_state(AnonymousSurveyState.waiting_for_option)


@router.message(AnonymousSurveyState.waiting_for_option)
async def add_options(message: types.Message, state: FSMContext):
    """
    Добавляем варианты ответа для последнего вопроса.
    """
    options = [opt.strip() for opt in message.text.split(";") if opt.strip()]
    valid_options = validate_options(options)

    if not valid_options:
        await message.answer(" Должно быть от 2 до 10 уникальных вариантов ответа.")
        return

    data = await state.get_data()
    survey_data = data.get("survey_data", {})

    if not survey_data.get("questions"):
        await message.answer(" Ошибка: вопросы не найдены. Попробуйте заново.")
        return

    last_question = survey_data["questions"][-1]
    last_question["options"].extend(valid_options)
    await state.update_data(survey_data=survey_data)

    await message.answer(
        " Варианты добавлены. Хотите добавить ещё вопрос или выдать ключ?",
        reply_markup=anonymous_survey_keyboard()
    )
    await state.set_state(AnonymousSurveyState.confirm_add_question)
