from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def confirm_ocr_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📤 Отправить как есть")],
            [KeyboardButton(text="✏️ Редактировать вручную")],
            [KeyboardButton(text="🔙 Отменить")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        is_persistent=True
    )
