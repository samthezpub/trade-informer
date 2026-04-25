import asyncio
import logging
import sys

from core.adapters.MoexPriceProvider import MoexPriceProvider
from core.services.PositionMonitor import PositionMonitor
from core.adapters.TelegramNotifier import TelegramNotifier
from dotenv import load_dotenv
import os

# aigoram deps
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

# handlers
from bot.handlers.commands import CommandRouter
from bot.handlers.position import PositionHandler
from bot.handlers.reports import ReportHandler
from infrastructure.database.adapters.postgresql_database import PostgreSQLDatabase

# db
from infrastructure.repositories.user_repo import SQLAlchemyUserRepository

load_dotenv()

# constants
bot_token = os.getenv('BOT_TOKEN')
db_path = os.getenv('DB_PATH')

if not bot_token:
    raise ValueError('BOT_TOKEN is not set')
if not db_path:
    raise ValueError('DB_PATH is not set')

db = PostgreSQLDatabase(database_path=db_path)

price_provider = MoexPriceProvider()
monitor = PositionMonitor(price_provider)
notifier = TelegramNotifier()


async def main() -> None:
    await db.create_tables()
    session = await db.get_session()

    # Repositories
    user_repository = SQLAlchemyUserRepository(session)

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # handlers
    command_router = CommandRouter(user_repository=user_repository)
    position_handler = PositionHandler(monitor, telegram_notifier=notifier, user_repository=user_repository)
    report_handler = ReportHandler(position_monitor=monitor, notifier=notifier, user_repository=user_repository)

    # Инклюды
    dp.include_router(command_router.router)
    dp.include_router(position_handler.router)
    dp.include_router(report_handler.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
