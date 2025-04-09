from database.tables.survey_data import Survey, SurveyQuestion, SurveyResponse
from database.tables.users import User


async def calculate_survey_results(survey_id: int) -> str:
    """
    Подсчитывает результаты опроса:
    - Количество участников.
    - Проценты голосов по каждому варианту ответа.
    """
    # Получаем опрос по ID, сразу подгружая связанные вопросы и их варианты ответов
    survey = await Survey.get_or_none(id=survey_id).prefetch_related("questions__answer_options")
    if not survey:
        return "❌ Опрос не найден."

    # Считаем общее количество голосов по всем вопросам опроса
    total_votes = await SurveyResponse.filter(
        question__survey_id=survey_id
    ).count()

    if total_votes == 0:
        # Если никто не проголосовал, уведомляем об этом
        return "❌ В этом опросе пока нет ответов."

    # Начинаем формировать итоговый текст с результатами
    result_text = [f"📊 Итоги опроса \"{survey.survey_title}\":", f"👥 Участвовало: {total_votes} человек\n"]

    # Получаем все вопросы опроса с их вариантами ответов
    questions = await SurveyQuestion.filter(survey=survey).prefetch_related("answer_options")

    for question in questions:
        # Добавляем текст вопроса
        result_text.append(f"❓ {question.question_text}")

        # Обрабатываем каждый вариант ответа для текущего вопроса
        for option in await question.answer_options.all():
            option_votes_qs = await SurveyResponse.filter(selected_option=option).all()
            option_votes = len(option_votes_qs)
            percentage = (option_votes / total_votes) * 100 if total_votes else 0

            # Строка с количеством голосов и процентом
            result_text.append(f"— {option.option_text}: {option_votes} голосов ({percentage:.1f}%)")

            # Добавляем имена проголосовавших
            for response in option_votes_qs:
                user = await User.get_or_none(telegram_id=response.user_id)
                user_name = user.full_name if user and user.full_name else f"ID {response.user_id}"
                result_text.append(f"    👤 {user_name}")

    # Собираем все строки результата в единый текст
    return "\n".join(result_text)
