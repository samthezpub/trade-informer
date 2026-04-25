import asyncio
import os

# aigoram deps
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from loguru import logger

# handlers
from bot.handlers.commands import CommandRouter
from bot.handlers.position import PositionHandler
from bot.handlers.reports import ReportHandler
from bot.middlewares.ThrottlingMidleware import ThrottlingMiddleware
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

# constants rate limit
time_for_update_limit_in_secs = int(os.getenv('TIME_FOR_UPDATE_LIMIT_IN_SECS'))
requests_per_limit = int(os.getenv('REQUEST_PER_LIMIT'))

if not bot_token:
    raise ValueError('BOT_TOKEN is not set')
if not db_path:
    raise ValueError('DB_PATH is not set')

db = PostgreSQLDatabase(database_path=db_path)

price_provider = MoexPriceProvider()
monitor = PositionMonitor(price_provider)
notifier = TelegramNotifier()


async def main() -> None:
    logger.debug("Инициализация приложения...")
    logger.debug("Создаём сессию...")
    session = await db.get_session()

    logger.debug("Подтягиваем зависимости...")
    # Repositories
    user_repository = SQLAlchemyUserRepository(session)

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # handlers
    command_router = CommandRouter(user_repository=user_repository)
    position_handler = PositionHandler(monitor, telegram_notifier=notifier, user_repository=user_repository)
    report_handler = ReportHandler(position_monitor=monitor, notifier=notifier, user_repository=user_repository)

    # middlewares
    command_router.router.message.middleware(ThrottlingMiddleware(
        time_for_update_limit=time_for_update_limit_in_secs, requests_per_limit=requests_per_limit))
    position_handler.router.message.middleware(ThrottlingMiddleware(time_for_update_limit=time_for_update_limit_in_secs,
                                                                    requests_per_limit=requests_per_limit))
    report_handler.router.message.middleware(ThrottlingMiddleware(time_for_update_limit=time_for_update_limit_in_secs,
                                                                  requests_per_limit=requests_per_limit))

    # Инклюды
    dp.include_router(command_router.router)
    dp.include_router(position_handler.router)
    dp.include_router(report_handler.router)

    logger.debug("Запускаем рассылатель....")
    # Рассылатель
    scheduler = ReportScheduler(
        bot=bot,
        monitor=monitor,
        notifier=notifier,
        user_repo=user_repository,
        interval_seconds=notify_interval,
    )

    asyncio.create_task(scheduler.start())

    logger.debug("Запускаем цикл бота...")
    await dp.start_polling(bot)
    logger.debug("Приложение запущено!")


if __name__ == '__main__':
    logger.remove()
    logger.add("logs/bot_{time}.log", rotation="10 MB", retention='7 days',
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
               level="INFO")
    logger.add("logs/bot_{time:YYYY-MM-DD}.log",
               rotation="10 MB",
               retention="7 days",
               format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
               level="DEBUG")
    asyncio.run(main())
