from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_answer_confirm_keyboard():
    """Клавиатура с кнопкой подтверждения выбора"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
