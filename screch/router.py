from aiogram import Router
from screch.start_quiz import router as start_router
from screch.question_handler import router as question_router
from screch.answer_handler import router as answer_router
from keyboards.button_handlers.confirm_start import router as confirm_start_router

# Основной роутер модуля screch
router = Router()

# Подключаем вспомогательные роутеры:
router.include_router(start_router)           # для старта опроса
router.include_router(question_router)        # - для обработки вопросов
router.include_router(answer_router)          # - для обработки ответов
router.include_router(confirm_start_router)   # для подтверждения начала
