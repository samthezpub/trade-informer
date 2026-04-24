import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.handlers import MessageHandler
from aiogram.types import Message

from core.services.PositionMonitor import PositionMonitor
from core.adapters.TelegramNotifier import TelegramNotifier


class PositionHandler:
    def __init__(self, position_monitor: PositionMonitor, telegram_notifier: TelegramNotifier):
        self.router = Router()
        self.position_monitor = position_monitor
        self.telegram_notifier = telegram_notifier
        self._register_handlers()

    def _register_handlers(self):
        self.router.message(Command(commands=['add']))(self.add_position_coomand)

    async def add_position_coomand(self, message: Message):
        """Обработчик команды добавить позицию /add VTBR 93.91 8 growth% loss%"""
        logging.log(msg=message, level=logging.DEBUG)
        parts = message.text.split()
        if len(parts) < 4:
            await message.answer("❌ Неверный формат.\n"
                                 "Пример: /add VTBR 93.91 8 0.5 1.0\n"
                                 "Где: тикер цена покупки количество тейк-профит% стоп-лосс%")
            return

        try:
            stock = parts[1].upper()
            buy_price = float(parts[2])
            stock_count = int(parts[3])
            take_profit = float(parts[4])
            stop_loss = float(parts[5])
        except ValueError:
            await message.answer("Вероятно вы совершили ошибку при написании. Попробуйте указывать цены и проценты "
                                 "через точку.")
            return

        # TODO Сохранять в бдшку акции юзера
        result = self.position_monitor.check_position_pnl(stock, buy_price, stock_count, take_profit, stop_loss)
        if result:
            await message.answer(f"{stock} добавлен в портфель. (Цена покупки: {buy_price}. Кол-во: {stock_count})")
            return
        await message.answer(f"Не удалось найти {stock}")

    async def remove_position(self, message: Message):
        # TODO Убирать у юзера акцию
        pass