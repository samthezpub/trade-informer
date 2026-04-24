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

from bot.handlers.commands import router as commands_router
from bot.handlers.position import PositionHandler
from bot.handlers.reports import ReportHandler

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')

if not bot_token:
    raise ValueError('BOT_TOKEN is not set')

price_provider = MoexPriceProvider()
monitor = PositionMonitor(price_provider)
notifier = TelegramNotifier()


async def main() -> None:
    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # handlers
    position_handler = PositionHandler(monitor, telegram_notifier=notifier)
    report_handler = ReportHandler(position_monitor=monitor, notifier=notifier)

    # Инклюды
    dp.include_router(commands_router)
    dp.include_router(position_handler.router)
    dp.include_router(report_handler.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
