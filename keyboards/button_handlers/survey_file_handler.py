from aiogram import Router, types
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from config.state_config import  TestFromPdfState, SurveyFromPdfState
from creation_survey.PDF_creator.pdf_processor import process_pdf_document

router = Router()


@router.message(StateFilter(TestFromPdfState.waiting_for_pdf), lambda message: message.document is not None)
async def handle_test_pdf_upload(message: types.Message, state: FSMContext, bot: Bot):
    """ Получен PDF-файл для ТЕСТА """
    await process_pdf_document(message, state, bot)


@router.message(StateFilter(SurveyFromPdfState.waiting_for_pdf), lambda message: message.document is not None)
async def handle_survey_pdf_upload(message: types.Message, state: FSMContext, bot: Bot):
    """ Получен PDF-файл для ОПРОСА """
    await process_pdf_document(message, state, bot)


