from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import AnonymousSurveyState
from keyboards.button_handlers.question_controls import handle_anonymous_finish

router = Router()


@router.message(AnonymousSurveyState.confirm_add_question)
async def confirm_add_question(message: types.Message, state: FSMContext):
    """
    Завершаем создание опроса или продолжаем добавление вопросов.
    """
    if message.text == "Продолжить":
        await message.answer("Введите новый вопрос:")
        await state.set_state(AnonymousSurveyState.waiting_for_question)
    elif message.text == "Выдать ключ":
        await handle_anonymous_finish(message, state)
