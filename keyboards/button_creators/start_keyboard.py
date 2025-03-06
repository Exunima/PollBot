from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from profile.name_handler import check_and_ask_name, process_name, process_name_change


# Определяем состояния
class UserState(StatesGroup):
    waiting_for_name = State()
    confirm_name_change = State()


# Функция для создания клавиатуры
def create_start_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мой профиль")],
            [KeyboardButton(text="Создать опрос")],
            [KeyboardButton(text="Пройти опрос")]
        ],
        resize_keyboard=True
    )
    return keyboard


# Вызов функции проверки имени из name_handler.py
async def check_user_name(message: types.Message, state: FSMContext):
    await check_and_ask_name(message, state)


# Обработчик изменения имени
async def change_name_handler(message: types.Message, state: FSMContext):
    await process_name_change(message, state)


# Обработчик ввода нового имени
async def name_input_handler(message: types.Message, state: FSMContext):
    await process_name(message, state)
