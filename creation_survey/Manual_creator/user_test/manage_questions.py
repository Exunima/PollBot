from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import TestState
from datetime import datetime, timedelta
from database.tables.users import User
from creation_survey.Manual_creator.validate_input import is_valid_question, validate_duration, validate_options

router = Router()


# Устанавливаем время теста и создаем структуру test_data
@router.message(TestState.waiting_for_duration)
async def ask_first_question(message: types.Message, state: FSMContext):
    duration = validate_duration(message.text)

    if duration == -1:
        await message.answer("❌ Введите корректное число (0 - без ограничения, максимум 180 минут).")
        return

    end_time = datetime.now() + timedelta(minutes=duration) if duration > 0 else None
    data = await state.get_data()

    # Получаем пользователя из БД
    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user:
        await message.answer("❌ Ошибка: ваш профиль не найден.")
        return

    # Создаем test_data, если оно отсутствует
    test_data = data.get("test_data", {})

    if "questions" not in test_data:
        test_data["questions"] = []  # Добавляем пустой список вопросов

    # Проверяем, есть ли сохраненное название. Если нет — берем из state
    test_data["title"] = test_data.get("title", data.get("title", "Без названия"))
    test_data["creator_id"] = user.id
    test_data["duration_minutes"] = duration if duration > 0 else None
    test_data["attempts"] = data.get("attempts", 1)

    # Обновляем состояние
    await state.update_data(
        duration=duration,
        end_time=end_time.timestamp() if end_time else None,
        test_data=test_data
    )

    await message.answer("Введите первый вопрос для теста:")
    await state.set_state(TestState.waiting_for_question)


# Обработчик ввода вопроса
@router.message(TestState.waiting_for_question)
async def ask_answers(message: types.Message, state: FSMContext):
    data = await state.get_data()
    test_data = data.get("test_data", {})

    if "questions" not in test_data:
        test_data["questions"] = []  # Создаем список вопросов, если его нет

    existing_questions = [q["question_text"] for q in test_data["questions"]]

    if not is_valid_question(message.text, existing_questions):
        await message.answer("❌ Вопрос должен содержать не менее 5 символов и не повторяться.")
        return

    test_data["questions"].append({
        "question_text": message.text,
        "answers": []  # Подготовка для хранения ответов
    })

    await state.update_data(test_data=test_data)  # Обновляем `test_data`

    await message.answer("Введите варианты ответа, разделяя их `;` (пример: Python; Java; C++; JavaScript)")
    await state.set_state(TestState.waiting_for_answers)


# Обработчик ввода вариантов ответа
@router.message(TestState.waiting_for_answers)
async def save_answers(message: types.Message, state: FSMContext):
    """
    Шаг, где пользователь вводит варианты ответа через `;`.
    Сохраняем их и просим выбрать номера правильных ответов.
    """
    options = [opt.strip() for opt in message.text.split(";") if opt.strip()]
    valid_options = validate_options(options)

    if not valid_options:
        await message.answer("❌ Должно быть от 2 до 10 уникальных вариантов ответа. Попробуйте снова.")
        return

    data = await state.get_data()
    test_data = data.get("test_data", {})

    # Проверяем, что test_data существует и содержит список вопросов
    if "questions" not in test_data:
        test_data["questions"] = []  # Создаем пустой список, если его нет

    if not test_data["questions"]:
        await message.answer("❌ Ошибка: вопросы не найдены. Начните тест заново.")
        return

    # Сохраняем варианты ответа в последний вопрос
    test_data["questions"][-1]["answers"] = valid_options
    await state.update_data(test_data=test_data, answers=valid_options)  # Обновляем state, включая answers

    # Формируем сообщение со списком вариантов
    answers_list = "\n".join([f"{i + 1}. {ans}" for i, ans in enumerate(valid_options)])

    await message.answer(
        f"Введите номера правильных ответов через `;` (например: 1;3).\n\nВарианты:\n{answers_list}"
    )
    await state.set_state(TestState.waiting_for_correct_answers)
