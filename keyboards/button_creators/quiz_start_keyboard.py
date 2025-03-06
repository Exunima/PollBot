from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Клавиатура для подтверждения начала теста/опроса
def get_quiz_start_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начать")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard
