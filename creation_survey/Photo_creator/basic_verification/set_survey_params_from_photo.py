from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import SurveyFromPhotoState
from creation_survey.Manual_creator import validate_input
from creation_survey.Photo_creator.photo_processor import process_photo_document
from aiogram import Bot

router = Router()


@router.message(SurveyFromPhotoState.waiting_for_duration)
async def get_duration_for_survey_photo(message: types.Message, state: FSMContext):
    value = validate_input.validate_days(message.text)
    if value == 0:
        await message.answer("❌ Введите число от 1 до 365.")
        return

    await state.update_data(duration_days=value)
    await state.set_state(SurveyFromPhotoState.waiting_for_photo)
    await message.answer("📎 Теперь отправьте фото с опросом.")


@router.message(SurveyFromPhotoState.waiting_for_photo, lambda m: m.photo or (m.document and m.document.mime_type.startswith("image/")))
async def handle_survey_photo_upload(message: types.Message, state: FSMContext, bot: Bot):
    await process_photo_document(message, state, bot)
