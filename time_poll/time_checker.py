from datetime import datetime, timedelta, timezone
from database.tables.test_data import Test, TestResponse
from database.tables.survey_data import Survey
from aiogram import Bot


async def check_test_time_and_attempts(user_id: int, test_id: int, start_time: datetime, bot: Bot):
    """
    Проверяем истечение времени теста и количество попыток пользователя.
    """
    test = await Test.get_or_none(id=test_id)
    if not test:
        return False

    now = datetime.now(timezone.utc)

    # Проверка времени
    if test.duration_minutes:
        end_time = start_time + timedelta(minutes=test.duration_minutes)
        if now >= end_time:
            # Если время вышло — завершаем тест для пользователя
            await finish_test_for_user(user_id, bot)  # ✅ Убираем передачу test_id
            return False

    # Проверка попыток
    user_attempts = await TestResponse.filter(
        user_id=user_id,
        question__test_id=test_id
    ).distinct().count()

    if test.attempts and user_attempts >= test.attempts:
        await block_test_for_user(user_id, test_id, bot)
        return False

    return True


async def finish_test_for_user(user_id: int, bot: Bot):
    """
    Завершает тест и выводит результат пользователю.
    """
    correct_count = await TestResponse.filter(
        user_id=user_id,
        is_correct=True
    ).count()

    total_questions = await TestResponse.filter(
        user_id=user_id
    ).distinct().count()

    result = f"⏰ Время вышло! Тест завершен.\nВаш результат: {correct_count} из {total_questions}."
    await bot.send_message(chat_id=user_id, text=result)


async def block_test_for_user(user_id: int, test_id: int, bot: Bot):
    """
    Блокирует тест при превышении попыток.
    """
    await bot.send_message(
        chat_id=user_id,
        text="❌ Лимит попыток на прохождение теста исчерпан. Доступ к тесту закрыт."
    )


async def check_survey_expiration(survey: Survey) -> bool:
    """
    Проверка окончания срока опроса.
    """
    now = datetime.now(timezone.utc)
    return now >= survey.get_expiration_date()
