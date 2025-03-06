from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from database.tables.survey_data import SurveyAnswerOption
from database.tables.test_data import TestAnswerOption
from config.state_config import QuizState
from keyboards.button_creators.quiz_answer_keyboard import get_answer_confirm_keyboard

router = Router()


# Задаем пользователю вопрос с вариантами ответов
async def ask_question(message: types.Message, state: FSMContext, quiz_type, question):
    options = await (SurveyAnswerOption.filter(question_id=question.id) if quiz_type == "survey"
                     else TestAnswerOption.filter(question_id=question.id))

    if not options:
        await message.answer("❌ Ошибка! У этого вопроса нет вариантов ответа.")
        await state.clear()
        return

    # Формируем список вариантов ответа
    options_list = "\n".join([f"{i + 1}. {opt.option_text}" for i, opt in enumerate(options)])
    options_map = {str(i + 1): opt.id for i, opt in enumerate(options)}

    await state.update_data(current_options=options_map)

    await message.answer(
        f"❓ {question.question_text}\n\nВарианты:\n{options_list}"
        f"\n\nВведите номера выбранных вариантов через ';', затем нажмите Enter или Отправить.",
        reply_markup=get_answer_confirm_keyboard()
    )
    await state.set_state(QuizState.waiting_for_answer)
