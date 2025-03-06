import asyncio
from database.base import init_db


async def main():
    await init_db()
    print(" База данных успешно инициализирована!")

if __name__ == "__main__":
    asyncio.run(main())
