# profile/name_handler.py
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Важно: импортируем User, а не Survey
from database.tables.users import User
from config.state_config import UserState


# Функция проверки и запроса имени
async def check_and_ask_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await User.filter(telegram_id=user_id).first()

    if user_data and user_data.full_name:
        from keyboards.button_creators.start_keyboard import create_start_keyboard
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Да, изменить")],
                [KeyboardButton(text="Нет, оставить текущее")]
            ],
            resize_keyboard=True
        )
        await message.answer(
            f"Ваше текущее имя: {user_data.full_name}\nХотите изменить его?",
            reply_markup=keyboard
        )
        await state.set_state(UserState.confirm_name_change)
    else:
        await message.answer("Введите ваше имя (оно будет использоваться для прохождения тестов):")
        await state.set_state(UserState.waiting_for_name)


# Обработчик выбора "Да" или "Нет"
async def process_name_change(message: types.Message, state: FSMContext):
    if message.text == "Да, изменить":
        await message.answer("Введите новое имя:")
        await state.set_state(UserState.waiting_for_name)
    else:
        from keyboards.button_creators.start_keyboard import create_start_keyboard
        keyboard = create_start_keyboard()
        await message.answer("Имя оставлено без изменений. Выберите действие:", reply_markup=keyboard)
        await state.clear()


# Обработчик ввода нового имени
async def process_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.text

    user_data, created = await User.get_or_create(
        telegram_id=user_id,
        defaults={"full_name": name}
    )
    if not created:
        # Если запись уже была, просто обновим full_name
        user_data.full_name = name
        await user_data.save()

    from keyboards.button_creators.start_keyboard import create_start_keyboard
    keyboard = create_start_keyboard()
    await message.answer(f"Спасибо, {name}! Теперь вы можете проходить тесты.", reply_markup=keyboard)
    await state.clear()


# Функция для получения имени пользователя (используется в p_profile.py)
async def get_user_name(telegram_id: int) -> str:
    user_data = await User.filter(telegram_id=telegram_id).first()
    return user_data.full_name if user_data and user_data.full_name else "Имя не указано"
