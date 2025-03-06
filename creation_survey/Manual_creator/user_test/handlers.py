from aiogram import Router

from creation_survey.Manual_creator.user_test.start_test import router as start_router
from creation_survey.Manual_creator.user_test.set_test_params import router as params_router
from creation_survey.Manual_creator.user_test.manage_questions import router as questions_router
from creation_survey.Manual_creator.user_test.finalize_test import router as finalize_router

router = Router()

# Подключаем все обработчики создания теста
router.include_router(start_router)
router.include_router(params_router)
router.include_router(questions_router)
router.include_router(finalize_router)
