from aiogram.fsm.state import StatesGroup, State


# Определяем состояния пользователя
class UserState(StatesGroup):
    waiting_for_name = State()
    confirm_name_change = State()


class TestState(StatesGroup):
    waiting_for_duration = State()
    waiting_for_question = State()
    waiting_for_answers = State()
    continue_or_finish = State()
    waiting_for_correct_answers = State()
    waiting_for_title = State()
    waiting_for_attempts = State()


class AnonymousSurveyState(StatesGroup):
    waiting_for_title = State()
    waiting_for_question = State()
    waiting_for_option = State()
    confirm_add_question = State()
    waiting_for_days = State()


class QuizState(StatesGroup):
    waiting_for_key = State()        # Ожидание ключа для теста/опроса
    confirm_start = State()          # Подтверждение начала
    waiting_for_answer = State()     # Ожидание ответа пользователя


class SurveyState(StatesGroup):
    waiting_for_pdf = State()
    waiting_for_photo = State()
    confirming_survey = State()


class TestFromPdfState(StatesGroup):
    waiting_for_duration = State()
    waiting_for_attempts = State()
    waiting_for_pdf = State()


class SurveyFromPdfState(StatesGroup):
    waiting_for_duration = State()
    waiting_for_pdf = State()


class TestFromPhotoState(StatesGroup):
    waiting_for_duration = State()
    waiting_for_attempts = State()
    waiting_for_photo = State()


class SurveyFromPhotoState(StatesGroup):
    waiting_for_duration = State()
    waiting_for_photo = State()
