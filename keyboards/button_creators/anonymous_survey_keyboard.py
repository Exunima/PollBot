from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def anonymous_survey_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Продолжить")],
            [KeyboardButton(text="Выдать ключ")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        is_persistent = True
    )
