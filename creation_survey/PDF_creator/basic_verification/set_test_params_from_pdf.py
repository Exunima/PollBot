from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import TestFromPdfState
from creation_survey.Manual_creator import validate_input

router = Router()


@router.message(TestFromPdfState.waiting_for_duration)
async def ask_attempts(message: types.Message, state: FSMContext):
    value = validate_input.validate_duration(message.text)
    if value == -1:
        await message.answer("❌ Введите число от 0 до 180.")
        return
    await state.update_data(duration_minutes=value)
    await state.set_state(TestFromPdfState.waiting_for_attempts)
    await message.answer("🔁 Укажите количество попыток (0 — неограниченно):")


@router.message(TestFromPdfState.waiting_for_attempts)
async def ready_to_upload_pdf(message: types.Message, state: FSMContext):
    value = validate_input.validate_attempts(message.text)
    if value == -1:
        await message.answer("❌ Введите число от 0 до 10.")
        return
    await state.update_data(attempts=value)
    await state.set_state(TestFromPdfState.waiting_for_pdf)
    await message.answer("📎 Отправьте PDF-файл с тестом.")
