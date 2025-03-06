from aiogram import Router

# Импортируем все обработчики анонимного опроса по этапам
from creation_survey.Manual_creator.anonim_opros.start_anon_survey import router as start_router
from creation_survey.Manual_creator.anonim_opros.validate_anon_survey import router as validate_router
from creation_survey.Manual_creator.anonim_opros.question_handler import router as question_router
from creation_survey.Manual_creator.anonim_opros.finish_anon_survey import router as finish_router

router = Router()

# Подключаем обработчики из отдельных файлов
router.include_router(start_router)
router.include_router(validate_router)
router.include_router(question_router)
router.include_router(finish_router)
