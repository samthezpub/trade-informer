from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from core.adapters.TelegramNotifier import TelegramNotifier
from core.services.PositionMonitor import PositionMonitor
from infrastructure.repositories.user_repo import SQLAlchemyUserRepository


class ReportHandler:
    def __init__(self, position_monitor: PositionMonitor, notifier: TelegramNotifier,
                 user_repository: SQLAlchemyUserRepository):
        self.position_monitor = position_monitor
        self.notifier = notifier
        self.router = Router()
        self.user_repository = user_repository
        self._register_handlers()

    def _register_handlers(self):
        self.router.message(Command(commands=['report']))(self.generate_report)

    async def generate_report(self, message: Message):
        chat_id = str(message.chat.id)
        stocks = await self.user_repository.get_user_stocks_by_telegram_id(telegram_id=chat_id)
        results = []

        for stock in stocks:
            result = self.position_monitor.check_position_pnl(stock_id=stock.id, stock=stock.ticket,
                                                              your_buy_price=stock.buy_price, stock_count=stock.count,
                                                              growth_threshold=stock.take_profit, loss_threshold=stock.stop_loss)
            if result:
                results.append(result)
            else:
                continue

        if not results:
            await message.answer("Нет активных позиций для отображения.")
            return

        formatted_message = self.notifier.format_report(results)
        await message.answer(formatted_message, parse_mode=ParseMode.HTML)
