import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import get_settings
from database import get_db
from database.models import Database
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.booking import router as booking_router
from handlers.crud import router as crud_router
from middlewares.logging import LoggingMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("hotel_bot")


async def main() -> None:
    settings = get_settings()
    database = get_db()
    database.create_tables()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(LoggingMiddleware())

    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(booking_router)
    dp.include_router(crud_router)

    logger.info("Бот запущен")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())