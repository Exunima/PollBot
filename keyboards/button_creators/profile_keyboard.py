from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_profile_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Показать имя")],
            [KeyboardButton(text="Сменить имя")],
            [KeyboardButton(text="Мои тесты")],
            [KeyboardButton(text="Мои опросы")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Выберите действие",
    )
    return keyboard
