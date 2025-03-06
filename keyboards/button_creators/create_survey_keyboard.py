from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_survey_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ввести вручную")],
            [KeyboardButton(text="Отправить PDF")],
            [KeyboardButton(text="Отправить фото")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard
