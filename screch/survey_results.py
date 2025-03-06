from database.tables.survey_data import Survey, SurveyQuestion, SurveyResponse


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
            # Подсчитываем количество голосов за этот вариант
            option_votes = await SurveyResponse.filter(selected_option=option).count()
            # Вычисляем процент голосов
            percentage = (option_votes / total_votes) * 100 if total_votes else 0
            # Добавляем информацию по каждому варианту в результат
            result_text.append(f"— {option.option_text}: {option_votes} голосов ({percentage:.1f}%)")

        result_text.append("")  # Добавляем пустую строку между вопросами

    # Собираем все строки результата в единый текст
    return "\n".join(result_text)
