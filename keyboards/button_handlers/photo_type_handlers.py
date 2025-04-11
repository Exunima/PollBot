from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import TestFromPhotoState, SurveyFromPhotoState
from keyboards.button_creators.choose_photo_doc_type_keyboard import choose_photo_doc_type_keyboard
from creation_survey.Photo_creator.photo_processor import process_photo_document
from aiogram import Bot

router = Router()


@router.message(lambda m: m.text == "Отправить фото")
async def choose_type_for_photo(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип документа, загружаемого по фото:", reply_markup=choose_photo_doc_type_keyboard())


@router.message(lambda m: m.text == "📘 Тест (фото)")
async def start_test_photo(message: types.Message, state: FSMContext):
    await state.update_data(document_type="test")
    await state.set_state(TestFromPhotoState.waiting_for_duration)
    await message.answer("⏱️ Сколько времени будет на тест? (в минутах)")


@router.message(TestFromPhotoState.waiting_for_photo, lambda m: m.photo or (m.document and m.document.mime_type.startswith("image/")))
async def handle_test_photo_upload(message: types.Message, state: FSMContext, bot: Bot):
    await process_photo_document(message, state, bot)


@router.message(lambda m: m.text == "📋 Опрос (фото)")
async def start_survey_photo(message: types.Message, state: FSMContext):
    await state.update_data(document_type="survey")
    await state.set_state(SurveyFromPhotoState.waiting_for_duration)
    await message.answer("📅 Сколько дней будет доступен опрос?")


@router.message(SurveyFromPhotoState.waiting_for_photo, lambda m: m.photo or (m.document and m.document.mime_type.startswith("image/")))
async def handle_survey_photo_upload(message: types.Message, state: FSMContext, bot: Bot):
    await process_photo_document(message, state, bot)
