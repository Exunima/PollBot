from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def choose_photo_doc_type_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Тест (фото)")],
            [KeyboardButton(text="📋 Опрос (фото)")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return keyboard
