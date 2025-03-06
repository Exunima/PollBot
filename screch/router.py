from aiogram import Router
from screch.start_quiz import router as start_router
from screch.question_handler import router as question_router
from screch.answer_handler import router as answer_router
from keyboards.button_handlers.confirm_start import router as confirm_start_router

router = Router()
router.include_router(start_router)
router.include_router(question_router)
router.include_router(answer_router)
router.include_router(confirm_start_router)
