from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import TestState
from user_profile.name_handler import check_and_ask_name
from database.tables.users import User

router = Router()


#  Обработчик начала создания теста с названием
@router.message(lambda message: message.text == "Тест")
async def ask_test_title(message: types.Message, state: FSMContext):
    user_data = await User.get_or_none(telegram_id=message.from_user.id)
    if not user_data or not user_data.full_name:
        await check_and_ask_name(message, state)
        return

    await message.answer("Введите название теста:")
    await state.set_state(TestState.waiting_for_title)
