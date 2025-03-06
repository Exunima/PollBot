from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Клавиатура для подтверждения начала теста/опроса
def get_quiz_start_keyboard():
    """Функция для создания клавиатуры перед началом теста/опроса"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начать")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard
