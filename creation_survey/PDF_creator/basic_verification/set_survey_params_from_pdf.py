from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from config.state_config import SurveyFromPdfState
from creation_survey.Manual_creator import validate_input

router = Router()


@router.message(SurveyFromPdfState.waiting_for_duration)
async def ready_to_upload_pdf(message: types.Message, state: FSMContext):
    value = validate_input.validate_days(message.text)
    if value == 0:
        await message.answer("❌ Введите число от 1 до 365.")
        return
    await state.update_data(duration=value)
    await state.set_state(SurveyFromPdfState.waiting_for_pdf)
    await message.answer("📎 Отправьте PDF-файл с опросом.")
