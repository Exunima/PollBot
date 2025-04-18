from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import ConfirmOCRState
from creation_survey.Photo_creator.photo_processor import process_clean_text_after_ocr
from aiogram import Bot
from keyboards.button_creators.choose_photo_doc_type_keyboard import choose_photo_doc_type_keyboard

router = Router()


@router.message(ConfirmOCRState.waiting_for_choice, lambda m: m.text == "📤 Отправить как есть")
async def confirm_send_as_is(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    extracted_text = data.get("extracted_text", "")
    await process_clean_text_after_ocr(message, state, bot, extracted_text)


@router.message(ConfirmOCRState.waiting_for_choice, lambda m: m.text == "✏️ Редактировать вручную")
async def edit_text_manually(message: types.Message, state: FSMContext):
    await message.answer("✏️ Пожалуйста, отправьте исправленный текст.")
    await state.set_state(ConfirmOCRState.waiting_for_manual_text)


@router.message(ConfirmOCRState.waiting_for_choice, lambda m: m.text == "🔙 Отменить")
async def cancel_ocr_flow(message: types.Message, state: FSMContext):
    await message.answer(
        "❌ Обработка отменена. Вернулись к выбору типа документа:",
        reply_markup=choose_photo_doc_type_keyboard()
    )
    await state.clear()


@router.message(ConfirmOCRState.waiting_for_manual_text)
async def handle_manual_ocr_text(message: types.Message, state: FSMContext, bot: Bot):
    await process_clean_text_after_ocr(message, state, bot, message.text)
