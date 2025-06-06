from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from keyboards.button_creators.create_survey_keyboard import create_survey_keyboard
from keyboards.button_creators.survey_type_keyboard import survey_type_keyboard
from screch.start_quiz import ask_quiz_key
import logging

# Роутер для управления созданием опросов
router = Router()


@router.message(lambda message: message.text and message.text.lower().strip() == "создать опрос")
async def start_survey_creation(message: types.Message, state: FSMContext):
    """Обработчик кнопки 'Создать опрос' – отправляет клавиатуру с методами создания."""
    try:
        logging.info(f"[DEBUG] Пользователь {message.from_user.id} начал создание опроса")
        await state.clear()  # Очищаем FSM перед началом создания
        await message.answer("Выберите способ создания опроса:", reply_markup=create_survey_keyboard())
    except Exception as e:
        logging.error(f"Ошибка при создании опроса у пользователя {message.from_user.id}: {e}")


@router.message(lambda message: message.text and message.text.lower().strip() == "ввести вручную")
async def manual_survey_creation(message: types.Message, state: FSMContext):
    """Обработчик кнопки 'Ввести вручную' – предлагает выбрать тип опроса."""
    try:
        logging.info(f"[DEBUG] Пользователь {message.from_user.id} выбрал ввод вручную")
        await state.clear()  # Очищаем FSM перед переходом
        await message.answer("Выберите тип опроса:", reply_markup=survey_type_keyboard())
    except Exception as e:
        logging.error(f"Ошибка при выборе типа опроса у пользователя {message.from_user.id}: {e}")


@router.message(lambda message: message.text and message.text.lower().strip() == "пройти опрос")
async def start_quiz_from_button(message: types.Message, state: FSMContext):
    """Переход к прохождению опроса по кнопке. Запрашиваем у пользователя ключ доступа."""
    try:
        await ask_quiz_key(message, state)
    except Exception as e:
        logging.error(f"Ошибка при запуске прохождения опроса у пользователя {message.from_user.id}: {e}")
