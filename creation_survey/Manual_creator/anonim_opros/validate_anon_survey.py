from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import AnonymousSurveyState
from creation_survey.Manual_creator.validate_input import (
    is_valid_title,
    validate_days
)

router = Router()


@router.message(AnonymousSurveyState.waiting_for_title)
async def ask_survey_duration_days(message: types.Message, state: FSMContext):
    """
    Сохраняем название опроса и запрашиваем его длительность в днях.
    """
    title = message.text.strip()

    if not is_valid_title(title):
        await message.answer(" Название должно содержать от 3 до 100 символов и не включать спецсимволы.")
        return

    data = await state.get_data()
    survey_data = data.get("survey_data", {})
    survey_data["title"] = title
    survey_data["questions"] = []
    survey_data["attempts"] = 1

    await state.update_data(survey_data=survey_data)
    await message.answer("Сколько дней будет длиться ваш опрос? (Введите число)")
    await state.set_state(AnonymousSurveyState.waiting_for_days)


@router.message(AnonymousSurveyState.waiting_for_days)
async def get_survey_days(message: types.Message, state: FSMContext):
    """
    Сохраняем длительность опроса и переходим к добавлению вопросов.
    """
    days_str = message.text.strip()
    duration_days = validate_days(days_str)

    if duration_days == 0:
        await message.answer(" Введите число от 1 до 365.")
        return

    data = await state.get_data()
    survey_data = data.get("survey_data", {})
    survey_data["duration_days"] = duration_days

    await state.update_data(survey_data=survey_data)
    await message.answer("Введите первый вопрос:")
    await state.set_state(AnonymousSurveyState.waiting_for_question)
