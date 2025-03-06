from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from database.tables.survey_data import SurveyQuestion
from database.tables.test_data import TestQuestion
from config.state_config import QuizState
from screch.question_handler import ask_question

router = Router()


# Обработчик кнопки "Начать"
@router.message(QuizState.confirm_start)
async def confirm_start_quiz(message: types.Message, state: FSMContext):
    if message.text.strip() == "Начать":
        data = await state.get_data()
        quiz_id, quiz_type = data["quiz_id"], data["quiz_type"]

        question = await (SurveyQuestion.filter(survey_id=quiz_id).first() if quiz_type == "survey"
                          else TestQuestion.filter(test_id=quiz_id).first())

        if not question:
            await message.answer("❌ Вопросы не найдены.")
            await state.clear()
            return

        await state.update_data(question_id=question.id)
        await ask_question(message, state, quiz_type, question)
