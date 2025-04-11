from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import TestFromPhotoState
from creation_survey.Manual_creator import validate_input
from creation_survey.Photo_creator.photo_processor import process_photo_document
from aiogram import Bot

router = Router()


@router.message(TestFromPhotoState.waiting_for_duration)
async def get_duration_for_test_photo(message: types.Message, state: FSMContext):
    value = validate_input.validate_duration(message.text)
    if value == -1:
        await message.answer("❌ Введите число от 0 до 180.")
        return

    await state.update_data(duration_minutes=value)
    await state.set_state(TestFromPhotoState.waiting_for_attempts)
    await message.answer("🔁 Укажите количество попыток (0 — неограниченно):")


@router.message(TestFromPhotoState.waiting_for_attempts)
async def get_attempts_for_test_photo(message: types.Message, state: FSMContext):
    value = validate_input.validate_attempts(message.text)
    if value == -1:
        await message.answer("❌ Введите число от 0 до 10.")
        return

    await state.update_data(attempts=value)
    await state.set_state(TestFromPhotoState.waiting_for_photo)
    await message.answer("📎 Теперь отправьте фото с тестом.")


@router.message(TestFromPhotoState.waiting_for_photo, lambda m: m.photo or (m.document and m.document.mime_type.startswith("image/")))
async def handle_test_photo_upload(message: types.Message, state: FSMContext, bot: Bot):
    await process_photo_document(message, state, bot)
