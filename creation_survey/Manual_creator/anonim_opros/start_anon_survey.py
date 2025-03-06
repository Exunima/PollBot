from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from database.tables.users import User
from profile.name_handler import check_and_ask_name
from config.state_config import AnonymousSurveyState

router = Router()


@router.message(lambda message: message.text.strip() == "Анонимный опрос")
async def start_anonymous_survey(message: types.Message, state: FSMContext):
    user = await User.get_or_none(telegram_id=message.from_user.id)

    if not user or not user.full_name:
        await check_and_ask_name(message, state)
        return

    await state.update_data(survey_data={"creator_id": user.id})
    await message.answer("Введите название вашего анонимного опроса:")
    await state.set_state(AnonymousSurveyState.waiting_for_title)
