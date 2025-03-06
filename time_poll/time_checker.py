from datetime import datetime, timedelta, timezone
from database.tables.test_data import Test, TestResponse
from database.tables.survey_data import Survey
from aiogram import Bot


async def check_test_time_and_attempts(user_id: int, test_id: int, start_time: datetime, bot: Bot):
    """
    Проверяет:
    1. Не истекло ли время, отведенное на тест.
    2. Не превышено ли количество попыток для прохождения теста.

    Если тест завершен по времени или по попыткам — отправляет уведомление пользователю и завершает проверку.
    """
    # Пытаемся найти тест в базе данных по ID
    test = await Test.get_or_none(id=test_id)
    if not test:
        # Тест не найден — дальнейшие проверки невозможны
        return False

    now = datetime.now(timezone.utc)

    # Проверяем ограничение по времени на тест
    if test.duration_minutes:
        end_time = start_time + timedelta(minutes=test.duration_minutes)
        if now >= end_time:
            # Время истекло — завершаем тест для пользователя
            await finish_test_for_user(user_id, bot)  # Убираем передачу test_id
            return False

    # Подсчитываем количество уникальных попыток пользователя для этого теста
    user_attempts = await TestResponse.filter(
        user_id=user_id,
        question__test_id=test_id
    ).distinct().count()

    # Проверяем ограничение по числу попыток
    if test.attempts and user_attempts >= test.attempts:
        # Лимит попыток исчерпан — блокируем тест для пользователя
        await block_test_for_user(user_id, test_id, bot)
        return False

    # Тест можно продолжать
    return True


async def finish_test_for_user(user_id: int, bot: Bot):
    """
    Завершает тест из-за истечения времени и отправляет пользователю результат.
    """
    # Подсчитываем количество правильных ответов пользователя
    correct_count = await TestResponse.filter(
        user_id=user_id,
        is_correct=True
    ).count()

    # Подсчитываем общее количество вопросов, на которые пользователь ответил
    total_questions = await TestResponse.filter(
        user_id=user_id
    ).distinct().count()

    # Формируем сообщение с результатом
    result = (
        f"⏰ Время вышло! Тест завершен.\n"
        f"Ваш результат: {correct_count} из {total_questions}."
    )

    # Отправляем результат пользователю
    await bot.send_message(chat_id=user_id, text=result)


async def block_test_for_user(user_id: int, test_id: int, bot: Bot):
    """
    Блокирует тест для пользователя при превышении лимита попыток и уведомляет об этом.
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
