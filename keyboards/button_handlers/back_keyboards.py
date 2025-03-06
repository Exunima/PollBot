from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from keyboards.button_creators.start_keyboard import create_start_keyboard

router = Router()


# Обработчик кнопки "Назад"
@router.message(lambda message: message.text == "🔙 Назад")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    """Очищает FSM и возвращает пользователя в главное меню."""
    await state.clear()  # Очистка всех состояний FSM перед возвратом в меню
    await message.answer(" Действие отменено. Возвращаемся в главное меню.", reply_markup=create_start_keyboard())
