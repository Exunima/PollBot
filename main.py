import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.exceptions import TelegramAPIError

# Импорт функций работы с базой данных
from database.base import init_db, close_db

# Импорт роутеров
from screch.router import router as quiz_router
from user_profile.p_profile import router as profile_router
from user_profile.name_handler import (
    check_and_ask_name,
    process_name,
    process_name_change
)
from keyboards.button_handlers.survey_file_handler import router as survey_file_router
from keyboards.button_handlers.back_keyboards import router as back_router
from keyboards.button_handlers.survey_handler import router as survey_router
from creation_survey.Manual_creator.user_test.handlers import router as create_survey_router
from creation_survey.Manual_creator.anonim_opros.anonim_survey_handler import router as anonim_survey_router
from creation_survey.Photo_creator.basic_verification.set_test_params_from_photo import router as test_photo_router
from creation_survey.Photo_creator.basic_verification.set_survey_params_from_photo import router as survey_photo_router
from keyboards.button_handlers.doc_type_handlers import router as doc_type_router
from keyboards.button_handlers.photo_type_handlers import router as photo_type_router

# Импорт состояний и токена
from config.state_config import UserState
from config.token_config import TOKEN


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Подключение к Redis для хранения состояний
try:
    storage = RedisStorage.from_url("redis://localhost:6379")
except Exception as e:
    logging.error(f"Ошибка подключения к Redis: {e}")
    storage = None  # Важно: без storage FSM может не работать!


# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

# Создаем основной роутер
router = Router()

# Регистрируем все роутеры
dp.include_router(router)
dp.include_router(profile_router)
dp.include_router(back_router)
dp.include_router(create_survey_router)
dp.include_router(survey_router)
dp.include_router(anonim_survey_router)
dp.include_router(quiz_router)
dp.include_router(survey_file_router)
dp.include_router(doc_type_router)
dp.include_router(photo_type_router)
dp.include_router(test_photo_router)
dp.include_router(survey_photo_router)


# Обработка команды /start — проверяем, указано ли имя пользователя
@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await check_and_ask_name(message, state)


# Обработка выбора о смене имени
@router.message(UserState.confirm_name_change)
async def change_name_handler(message: types.Message, state: FSMContext):
    await process_name_change(message, state)


# Обработка ввода нового имени
@router.message(UserState.waiting_for_name)
async def name_input_handler(message: types.Message, state: FSMContext):
    await process_name(message, state)


# Основная функция запуска бота с корректным закрытием ресурсов
async def main():
    await init_db()  # Подключение к базе данных
    try:
        logging.info("Бот запущен! Ожидаем сообщения...")
        await bot.delete_webhook(drop_pending_updates=True)  # Сбросим старые апдейты
        await dp.start_polling(bot)  # Запускаем цикл обработки сообщений
    except asyncio.CancelledError:
        logging.info("Бот остановлен.")
    except TelegramAPIError as error:
        logging.error(f"Ошибка API Telegram: {error}")
    except Exception as exc:
        logging.exception(f"Неизвестная ошибка: {exc}")
    finally:
        await bot.session.close()  # Закрытие сессии бота
        await close_db()  # Закрытие соединения с БД
        logging.info("Бот выключен.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем.")
