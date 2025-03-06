# Проверка корректности названия теста/опроса
def is_valid_title(title: str) -> bool:
    """
    Проверяет название теста/опроса:
    - Длина от 3 до 100 символов
    - Без спецсимволов (!@#$%^&*())
    """
    title = title.strip()
    if len(title) < 3 or len(title) > 100:
        return False
    if any(char in "!@#$%^&*()" for char in title):
        return False
    return True


# Проверка текста вопроса на уникальность и длину
def is_valid_question(question: str, existing_questions: list) -> bool:
    """
    Проверяет, что вопрос:
    - Не короче 5 символов
    - Не является дубликатом
    """
    question = question.strip()
    if len(question) < 5:
        return False
    if question in existing_questions:
        return False
    return True


# Проверка вариантов ответа (уникальность, количество)
def validate_options(options: list) -> list:
    """
    Проверяет варианты ответов:
    - Минимум 2 варианта
    - Максимум 10 вариантов
    - Исключает дубликаты и пустые ответы
    - Поддерживает числа
    """
    options = [opt.strip() for opt in options if opt.strip()]  # Убираем пустые строки
    options = list(set(options))  # Убираем дубликаты, но сохраняем числа

    return options if 2 <= len(options) <= 10 else []


# Проверка корректных номеров правильных ответов
def validate_correct_answers(correct_answers: str, total_answers: int) -> list:
    """
    Проверяет номера правильных ответов:
    - Только числа
    - Число не выходит за границы вариантов ответов
    """
    selected = [int(num.strip()) for num in correct_answers.split(";") if num.strip().isdigit()]
    return [num for num in selected if 1 <= num <= total_answers]


# Проверка количества дней для опроса
def validate_days(days: str) -> int:
    """
    Проверяет корректность количества дней для опроса.
    - Только числа
    - Диапазон 1-365 дней
    """
    if not days.isdigit():
        return 0
    days = int(days)
    return days if 1 <= days <= 365 else 0


# Проверка количества попыток
def validate_attempts(attempts: str) -> int:
    """
    Проверяет количество попыток для тестов:
    - Только числа
    - Диапазон 0-10 (0 = бесконечные попытки)
    """
    if not attempts.isdigit():
        return -1
    attempts = int(attempts)
    return attempts if 0 <= attempts <= 10 else -1


# Проверка продолжительности теста в минутах
def validate_duration(minutes: str) -> int:
    """
    Проверяет, сколько минут даётся на прохождение теста.
    - Только числа
    - Диапазон 0-180 (0 = без ограничения)
    """
    if not minutes.isdigit():
        return -1
    minutes = int(minutes)
    return minutes if 0 <= minutes <= 180 else -1
