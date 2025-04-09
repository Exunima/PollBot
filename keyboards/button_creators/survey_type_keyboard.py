from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def survey_type_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Тест")],
            [KeyboardButton(text="Анонимный опрос")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return keyboard
