import os
from tortoise import Tortoise

# Фиксированный путь к БД
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/db.sqlite3"))


async def init_db():
    """Инициализация базы данных"""
    await Tortoise.init(
        db_url=f"sqlite://{DB_PATH}",
        modules={"models": ["database.tables.users", "database.tables.survey_data", "database.tables.test_data"]}
    )
    await Tortoise.generate_schemas(safe=True)


async def close_db():
    """Закрываем соединение с БД"""
    await Tortoise.close_connections()
