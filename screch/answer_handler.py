from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from datetime import datetime
from database.tables.survey_data import SurveyAnswerOption, SurveyResponse, SurveyQuestion
from database.tables.test_data import TestResponse, TestQuestion, TestResult
from config.state_config import QuizState
from time_poll.time_checker import check_test_time_and_attempts
from .question_handler import ask_question

router = Router()


# Обработка ответа пользователя
@router.message(QuizState.waiting_for_answer)
async def process_test_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question_id = data["question_id"]
    quiz_id = data["quiz_id"]
    quiz_type = data["quiz_type"]
    start_time_str = data.get("start_time")
    start_time = datetime.fromisoformat(start_time_str) if start_time_str else None
    current_options = data.get("current_options", {})

    # Проверяем время и попытки, если это тест
    if quiz_type == "test":
        is_valid = await check_test_time_and_attempts(
            user_id=message.from_user.id,
            test_id=quiz_id,
            start_time=start_time,
            bot=message.bot
        )
        if not is_valid:
            await state.clear()
            return

    if quiz_type == "survey":
        # Проверяем и сохраняем ответ на опрос
        selected_num = message.text.strip()
        option_id = current_options.get(selected_num)

        if not option_id:
            await message.answer("❌ Ошибка! Введите номер из предложенных вариантов.")
            return

        answer_option = await SurveyAnswerOption.get_or_none(id=option_id)
        if not answer_option:
            await message.answer("❌ Ошибка! Вариант не найден.")
            return

        await SurveyResponse.create(
            question_id=question_id,
            user_id=message.from_user.id,
            selected_option=answer_option
        )

        # Переход к следующему вопросу
        next_question = await SurveyQuestion.filter(survey_id=quiz_id, id__gt=question_id).first()
        if next_question:
            await state.update_data(question_id=next_question.id)
            await ask_question(message, state, quiz_type, next_question)
        else:
            await message.answer("Спасибо за участие!")
            await state.clear()
        return

    # Проверка корректности ответов для тестов
    selected_numbers = [num.strip() for num in message.text.split(";")]
    selected_ids = [current_options.get(num) for num in selected_numbers if num in current_options]

    if not selected_ids:
        await message.answer("❌ Введите корректные номера из предложенных вариантов.")
        return

    question = await TestQuestion.get(id=question_id).prefetch_related("correct_answers")
    correct_options = {opt.id for opt in await question.correct_answers.all()}

    is_correct = set(selected_ids) == correct_options

    # Сохраняем ответы
    for option_id in selected_ids:
        await TestResponse.create(
            question_id=question_id,
            user_id=message.from_user.id,
            selected_option_id=option_id,
            is_correct=is_correct
        )

    # Переход к следующему вопросу или подсчет результатов
    next_question = await TestQuestion.filter(test_id=quiz_id, id__gt=question_id).first()
    if next_question:
        await state.update_data(question_id=next_question.id)
        await ask_question(message, state, "test", next_question)
    else:
        # Подсчет баллов
        correct_count = await TestResponse.filter(
            user_id=message.from_user.id,
            is_correct=True,
            question__test_id=quiz_id
        ).count()

        total_questions = await TestQuestion.filter(test_id=quiz_id).count()

        # Проверка и сохранение лучшего результата
        existing_result = await TestResult.get_or_none(
            test_id=quiz_id,
            user_id=message.from_user.id
        )

        if not existing_result:
            await TestResult.create(
                test_id=quiz_id,
                user_id=message.from_user.id,
                best_score=correct_count
            )
        else:
            if correct_count > existing_result.best_score:
                existing_result.best_score = correct_count
                await existing_result.save()

        # Исправляем удаление попыток
        if correct_count == total_questions:
            # Получаем все вопросы теста
            question_ids = await TestQuestion.filter(test_id=quiz_id).values_list('id', flat=True)

            # Удаляем все ответы пользователя на эти вопросы
            await TestResponse.filter(
                user_id=message.from_user.id,
                question_id__in=question_ids
            ).delete()

            await message.answer(
                f"🎉 Поздравляем! Вы набрали максимальный балл {correct_count} из {total_questions}."
                f"\nВаши попытки сброшены, так как тест пройден на максимум."
            )
        else:
            await message.answer(
                f"🎉 Тест завершен! Ваш результат: {correct_count} из {total_questions}."
            )

        await state.clear()
