from database.tables.test_data import Test, TestQuestion, TestResult
from database.tables.survey_data import Survey, SurveyQuestion
from database.tables.users import User
from screch.survey_results import calculate_survey_results


# Показываем пользователю список его тестов с результатами
async def show_user_tests(message):
    """Выводит список созданных пользователем тестов с результатами"""
    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user:
        await message.answer("❌ У вас нет созданных тестов.")
        return

    user_tests = await Test.filter(creator=user).all()
    if not user_tests:
        await message.answer("🔍 У вас пока нет созданных тестов.")
        return

    response = "📋 Ваши тесты с результатами пользователей:\n\n"
    for test in user_tests:
        questions = await TestQuestion.filter(test=test).all()
        if not questions or not test.title:
            continue

        response += (
            f"📝 Название: {test.title}\n"
            f"🔑 Ключ: `{test.access_key}`\n"
            f"🕒 Время: {test.duration_minutes if test.duration_minutes else 'Неограниченно'} минут\n"
            f"🔄 Попытки: {test.attempts if test.attempts else 'Неограниченно'}\n"
        )

        # Добавляем вывод лучших результатов пользователей
        test_results = await TestResult.filter(test=test).all()
        if test_results:
            response += "🏆 Лучшие результаты:\n"
            for result in test_results:
                test_user = await User.get_or_none(telegram_id=result.user_id)
                user_name = test_user.full_name if test_user and test_user.full_name else f"ID {result.user_id}"
                response += f"— {user_name}: {result.best_score} баллов\n"
        else:
            response += "❌ Нет результатов.\n"

        response += "---------------------------------\n"

    await message.answer(response, parse_mode="Markdown")


# Итоги пользователя и список его опросов
async def show_user_surveys(message):
    """Выводит список созданных пользователем опросов с актуальной статистикой"""
    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user:
        await message.answer("❌ У вас нет созданных опросов.")
        return

    user_surveys = await Survey.filter(creator=user).all()
    if not user_surveys:
        await message.answer("🔍 У вас пока нет созданных опросов.")
        return

    response = "📊 Ваши опросы с результатами:\n\n"
    for survey in user_surveys:
        questions = await SurveyQuestion.filter(survey=survey).all()
        if not questions or not survey.survey_title:
            continue

        response += (
            f"📝 Название: {survey.survey_title}\n"
            f"🔑 Ключ: `{survey.access_key}`\n"
            f"📅 Создан: {survey.created_at.strftime('%Y-%m-%d')}\n"
            f"🔄 Попытки: {survey.attempts}\n"
        )

        # Добавляем статистику по опросу
        survey_results = await calculate_survey_results(survey.id)
        response += f"{survey_results}\n"

        response += "---------------------------------\n"

    await message.answer(response, parse_mode="Markdown")
