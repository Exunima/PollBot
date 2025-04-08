from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import TestFromPdfState, SurveyFromPdfState
from keyboards.button_creators.choose_doc_type_keyboard import choose_doc_type_keyboard

router = Router()


@router.message(lambda m: m.text == "Отправить PDF")
async def ask_type(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип документа:", reply_markup=choose_doc_type_keyboard())


@router.message(lambda m: m.text == "📘 Тест")
async def start_test_pdf(message: types.Message, state: FSMContext):
    await state.update_data(document_type="test")
    await message.answer("⏱️ Сколько времени будет дано на прохождение теста? (в минутах, 0 — без ограничения)")
    await state.set_state(TestFromPdfState.waiting_for_duration)


@router.message(lambda m: m.text == "📋 Опрос")
async def start_survey_pdf(message: types.Message, state: FSMContext):
    await state.update_data(document_type="survey")
    await message.answer("📅 Укажите срок действия опроса в днях (0 — без ограничения):")
    await state.set_state(SurveyFromPdfState.waiting_for_duration)
