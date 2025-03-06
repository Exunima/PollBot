from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import TestState
from creation_survey.Manual_creator.validate_input import is_valid_title, validate_attempts, validate_duration

router = Router()


@router.message(TestState.waiting_for_title)
async def ask_attempts(message: types.Message, state: FSMContext):
    title = message.text.strip()

    if not is_valid_title(title):
        await message.answer("❌ Название теста должно содержать от 3 до 100 символов и не включать спецсимволы.")
        return

    data = await state.get_data()
    test_data = data.get("test_data", {})

    # ✅ Гарантированно сохраняем title в test_data
    test_data["title"] = title
    await state.update_data(test_data=test_data)

    await message.answer(
        "Сколько попыток разрешено для прохождения теста? (Введите 0 для неограниченного количества попыток)"
    )
    await state.set_state(TestState.waiting_for_attempts)


@router.message(TestState.waiting_for_attempts)
async def ask_test_duration(message: types.Message, state: FSMContext):
    attempts = validate_attempts(message.text)

    if attempts == -1:
        await message.answer("❌ Введите корректное число (0 - бесконечные попытки, максимум 10).")
        return

    data = await state.get_data()
    test_data = data.get("test_data", {})

    # ✅ Сохраняем attempts в test_data
    test_data["attempts"] = attempts

    await state.update_data(test_data=test_data)

    await message.answer("Сколько времени будет дано на прохождение теста? (в минутах, 0 — без ограничения)")
    await state.set_state(TestState.waiting_for_duration)


@router.message(TestState.waiting_for_duration)
async def ask_first_question(message: types.Message, state: FSMContext):
    duration = validate_duration(message.text)

    if duration == -1:
        await message.answer("❌ Введите корректное число (0 - без ограничения, максимум 180 минут).")
        return

    data = await state.get_data()
    test_data = data.get("test_data", {})

    # ✅ Сохраняем duration_minutes в test_data
    test_data["duration_minutes"] = duration

    await state.update_data(test_data=test_data)

    await message.answer("Введите первый вопрос:")
    await state.set_state(TestState.waiting_for_question)

