import asyncio
import logging
import os
import sys

# aigoram deps
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

# handlers
from bot.handlers.commands import CommandRouter
from bot.handlers.position import PositionHandler
from bot.handlers.reports import ReportHandler
from bot.schedulers.report_scheduler import ReportScheduler
from core.adapters.MoexPriceProvider import MoexPriceProvider
from core.adapters.TelegramNotifier import TelegramNotifier
from core.services.PositionMonitor import PositionMonitor
from infrastructure.database.adapters.postgresql_database import PostgreSQLDatabase
# db
from infrastructure.repositories.user_repo import SQLAlchemyUserRepository

load_dotenv()

# constants
bot_token = os.getenv('BOT_TOKEN')
db_path = os.getenv('DB_PATH')
notify_interval = int(os.getenv('NOTIFY_INTERVAL_SECS'))

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

    # Рассылатель
    scheduler = ReportScheduler(
        bot=bot,
        monitor=monitor,
        notifier=notifier,
        user_repo=user_repository,
        interval_seconds=notify_interval,
    )

    asyncio.create_task(scheduler.start())

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
