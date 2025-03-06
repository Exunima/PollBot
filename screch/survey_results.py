from database.tables.survey_data import Survey, SurveyQuestion, SurveyResponse


async def calculate_survey_results(survey_id: int) -> str:
    """
    Подсчитывает результаты опроса:
    - Количество участников.
    - Проценты голосов по каждому варианту ответа.
    """
    survey = await Survey.get_or_none(id=survey_id).prefetch_related("questions__answer_options")
    if not survey:
        return "❌ Опрос не найден."

    total_votes = await SurveyResponse.filter(
        question__survey_id=survey_id
    ).count()

    if total_votes == 0:
        return "❌ В этом опросе пока нет ответов."

    result_text = [f"📊 Итоги опроса \"{survey.survey_title}\":", f"👥 Участвовало: {total_votes} человек\n"]

    questions = await SurveyQuestion.filter(survey=survey).prefetch_related("answer_options")
    for question in questions:
        result_text.append(f"❓ {question.question_text}")

        for option in await question.answer_options.all():
            option_votes = await SurveyResponse.filter(selected_option=option).count()
            percentage = (option_votes / total_votes) * 100 if total_votes else 0
            result_text.append(f"— {option.option_text}: {option_votes} голосов ({percentage:.1f}%)")

        result_text.append("")  # Добавляем пустую строку между вопросами

    return "\n".join(result_text)
