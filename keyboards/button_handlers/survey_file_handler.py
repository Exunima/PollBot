from aiogram import Router, types
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from config.state_config import SurveyState
from keyboards.button_creators.create_survey_keyboard import create_survey_keyboard
from creation_survey.PDF_creator.pdf_processor import process_pdf_document
# from creation_survey.Photo_creator.photo_processor import process_photo_document  # Добавляем обработку фото

router = Router()


@router.message(StateFilter(SurveyState.waiting_for_pdf), lambda message: message.document is not None)
async def process_pdf_file(message: types.Message, state: FSMContext, bot: Bot):
    """ Пользователь отправил PDF """
    await process_pdf_document(message, state, bot)


@router.message(lambda message: message.text == "Отправить фото")
async def handle_photo_upload(message: types.Message, state: FSMContext):
    """ Пользователь нажал кнопку 'Отправить фото' """
    await state.set_state(SurveyState.waiting_for_photo)
    await message.answer(
        "📸 Пожалуйста, отправьте фото с тестом.",
        reply_markup=create_survey_keyboard()
    )


# @router.message(StateFilter(SurveyState.waiting_for_photo), lambda message: message.photo is not None)
# async def process_photo_file(message: types.Message, state: FSMContext):
#     """ Пользователь отправил фото """
#     await process_photo_document(message, state)
