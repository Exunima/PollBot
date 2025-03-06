import asyncio
import logging
from datetime import datetime, timezone
from database.base import init_db, close_db
from database.tables.survey_data import Survey
from database.tables.test_data import Test

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def cleanup_expired_records():
    now = datetime.now(timezone.utc)  # ✅ Теперь now учитывает временную зону UTC

    # Очистка устаревших опросов
    surveys = await Survey.all()
    deleted_surveys = 0
    for survey in surveys:
        expiry = survey.get_expiration_date()
        if now >= expiry:
            await survey.delete()
            deleted_surveys += 1

    logging.info(f"✅ Удалено устаревших опросов: {deleted_surveys}")

    # Очистка устаревших тестов
    tests = await Test.all()
    deleted_tests = 0
    for test in tests:
        expiry = test.get_expiration_date()
        if now >= expiry:
            await test.delete()
            deleted_tests += 1

    logging.info(f"✅ Удалено устаревших тестов: {deleted_tests}")


async def main():
    await init_db()
    await cleanup_expired_records()
    await close_db()

if __name__ == "__main__":
    asyncio.run(main())
