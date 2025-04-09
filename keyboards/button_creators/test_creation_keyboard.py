from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def test_creation_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Продолжить")],
            [KeyboardButton(text="Завершить")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return keyboard
