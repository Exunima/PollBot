from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import TestState
from keyboards.button_creators.test_creation_keyboard import test_creation_keyboard
from keyboards.button_handlers.question_controls import handle_continue, handle_finish
from creation_survey.Manual_creator.validate_input import validate_options, validate_correct_answers

router = Router()


# Завершение добавления вопросов и правильных ответов в тесте
@router.message(TestState.waiting_for_answers)
async def save_question(message: types.Message, state: FSMContext):
    """
    Сохраняем введенные варианты ответов в state.
    """
    # Проверяем введенные ответы
    raw_answers = [a.strip() for a in message.text.split(";") if a.strip()]
    valid_answers = validate_options(raw_answers)

    if not valid_answers:
        await message.answer("❌ Должно быть от 2 до 10 уникальных вариантов ответа. Введите снова:")
        return

    await state.update_data(answers=valid_answers)

    # Формируем текст со списком вариантов
    answers_list = "\n".join([f"{i + 1}. {ans}" for i, ans in enumerate(valid_answers)])
    await message.answer(
        f"Введите номера правильных ответов через `;` (например: 1;3).\n\nВарианты:\n{answers_list}"
    )
    await state.set_state(TestState.waiting_for_correct_answers)


@router.message(TestState.waiting_for_correct_answers)
async def save_correct_answers(message: types.Message, state: FSMContext):
    """
    Шаг, где пользователь указывает номера правильных ответов (например '1;3').
    Нужно сохранить их в текущем вопросе внутри test_data.
    """
    data = await state.get_data()
    answers = data.get("answers", [])  # answers точно берётся из state
    test_data = data.get("test_data", {})
    questions = test_data.get("questions", [])

    if not answers:
        await message.answer("❌ Ошибка: не найдены варианты ответов. Повторите ввод вопросов.")
        return
    if not questions:
        await message.answer("❌ Ошибка: список вопросов пуст. Начните создание теста заново.")
        return

    selected_answers = validate_correct_answers(message.text, len(answers))

    if not selected_answers:
        await message.answer("❌ Выберите хотя бы один правильный ответ, используя корректные номера.")
        return

    # Получаем последний вопрос (текущий)
    last_question = questions[-1]

    # Создаём список правильных ответов
    correct_answers_list = [answers[i - 1] for i in selected_answers]

    # Связываем правильные ответы с вопросом в ManyToMany
    last_question["correct_answers"] = correct_answers_list

    # Сохраняем обновленный вопрос в test_data
    questions[-1] = last_question
    test_data["questions"] = questions

    # Обновляем state
    await state.update_data(test_data=test_data)

    await message.answer(
        "Вопрос добавлен! Хотите ли вы добавить еще один вопрос?",
        reply_markup=test_creation_keyboard()
    )
    await state.set_state(TestState.continue_or_finish)


@router.message(TestState.continue_or_finish)
async def question_controls(message: types.Message, state: FSMContext):
    """
    Шаг, где пользователь может либо добавить следующий вопрос, либо завершить создание теста.
    """
    if message.text == "Продолжить":
        await handle_continue(message, state)
    elif message.text == "Завершить":
        await handle_finish(message, state)
