from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from core.adapters.TelegramNotifier import TelegramNotifier
from core.services.PositionMonitor import PositionMonitor


class ReportHandler:
    def __init__(self, position_monitor: PositionMonitor, notifier: TelegramNotifier):
        self.position_monitor = position_monitor
        self.notifier = notifier
        self.router = Router()
        self._register_handlers()

    def _register_handlers(self):
        self.router.message(Command(commands=['report']))(self.generate_report)

    async def generate_report(self, message: Message):
        # TODO брать из бдшки акции юзера
        stocks = ["SBER", "VTBR"]
        results = []

        for stock in stocks:
            result = self.position_monitor.check_position_pnl(stock, 10.1, 1, 5, 1)
            if result:
                results.append(result)
            else:
                continue

        if not results:
            await message.answer("Нет активных позиций для отображения.")
            return

        formatted_message = self.notifier.format_report(results)
        await message.answer(formatted_message, parse_mode=ParseMode.HTML)