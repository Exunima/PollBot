from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from datetime import datetime, timezone
from database.tables.survey_data import Survey
from database.tables.test_data import Test
from aiogram.filters import Command
from config.state_config import QuizState
from keyboards.button_creators.quiz_start_keyboard import get_quiz_start_keyboard
from time_poll.time_checker import check_survey_expiration

router = Router()


@router.message(Command("start_quiz"))
async def ask_quiz_key(message: types.Message, state: FSMContext):
    await message.answer("🔑 Введите ключ для прохождения опроса/теста:")
    await state.set_state(QuizState.waiting_for_key)


@router.message(QuizState.waiting_for_key)
async def check_quiz_key(message: types.Message, state: FSMContext):
    key = message.text.strip()
    survey = await Survey.get_or_none(access_key=key)
    test = await Test.get_or_none(access_key=key)

    if survey:
        if await check_survey_expiration(survey):
            await message.answer("❌ Время прохождения опроса истекло.")
            return
        quiz_type, quiz_id = "survey", survey.id
    elif test:
        quiz_type, quiz_id = "test", test.id
    else:
        await message.answer("❌ Неверный ключ! Попробуйте снова.")
        return

    await state.update_data(
        quiz_id=quiz_id,
        quiz_type=quiz_type,
        start_time=datetime.now(timezone.utc).isoformat()
    )
    await message.answer("Вы хотите начать прохождение?", reply_markup=get_quiz_start_keyboard())
    await state.set_state(QuizState.confirm_start)
