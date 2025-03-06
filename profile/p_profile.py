from aiogram import Router, types
from aiogram.fsm.context import FSMContext

# Импорт клавиатуры профиля
from keyboards.button_creators.profile_keyboard import create_profile_keyboard

# Импорты из базы данных и других модулей профиля
from profile.name_handler import get_user_name
from profile.show_tests import show_user_tests, show_user_surveys


router = Router()


# Обработчик кнопки "Мой профиль"
@router.message(lambda message: message.text == "Мой профиль")
async def show_profile_menu(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=create_profile_keyboard())


# Обработчик кнопки "Показать имя"
@router.message(lambda message: message.text == "Показать имя")
async def show_name(message: types.Message):
    user_name = await get_user_name(message.from_user.id)
    await message.answer(f"Ваше имя: {user_name}")


# Обработчик кнопки "Сменить имя"
@router.message(lambda message: message.text == "Сменить имя")
async def change_name(message: types.Message, state: FSMContext):
    from keyboards.button_creators.start_keyboard import check_user_name  # Избегаем циклического импорта
    await check_user_name(message, state)


# Обработчик кнопки "Мои тесты"
@router.message(lambda message: message.text == "Мои тесты")
async def handle_show_tests(message: types.Message):
    """Выводит список тестов пользователя"""
    await show_user_tests(message)


# Обработчик кнопки "Мои опросы"
@router.message(lambda message: message.text == "Мои опросы")
async def handle_show_surveys(message: types.Message):
    """Выводит список опросов пользователя"""
    await show_user_surveys(message)
