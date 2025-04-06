from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def choose_doc_type_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Тест")],
            [KeyboardButton(text="📋 Опрос")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )
