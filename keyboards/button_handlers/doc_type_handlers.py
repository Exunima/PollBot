from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import SurveyState
from keyboards.button_creators.choose_doc_type_keyboard import choose_doc_type_keyboard

router = Router()


@router.message(lambda m: m.text == "Отправить PDF")
async def ask_type(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип документа:", reply_markup=choose_doc_type_keyboard())


@router.message(lambda m: m.text == "📘 Тест")
async def set_test(message: types.Message, state: FSMContext):
    await state.update_data(document_type="test")
    await state.set_state(SurveyState.waiting_for_pdf)
    await message.answer("Отправьте PDF-файл с тестом.")


@router.message(lambda m: m.text == "📋 Опрос")
async def set_survey(message: types.Message, state: FSMContext):
    await state.update_data(document_type="survey")
    await state.set_state(SurveyState.waiting_for_pdf)
    await message.answer("Отправьте PDF-файл с опросом.")
