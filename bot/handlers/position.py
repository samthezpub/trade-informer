from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from core.adapters.TelegramNotifier import TelegramNotifier
from core.services.PositionMonitor import PositionMonitor
from infrastructure.repositories.user_repo import SQLAlchemyUserRepository


class PositionHandler:
    def __init__(self, position_monitor: PositionMonitor, telegram_notifier: TelegramNotifier,
                 user_repository: SQLAlchemyUserRepository):
        self.router = Router()
        self.position_monitor = position_monitor
        self.telegram_notifier = telegram_notifier
        self.user_repository = user_repository
        self._register_handlers()

    def _register_handlers(self):
        self.router.message(Command(commands=['add']))(self.add_position_coomand)
        self.router.message(Command(commands=['remove']))(self.remove_position)

    async def add_position_coomand(self, message: Message):
        """Обработчик команды добавить позицию /add VTBR 93.91 8 growth% loss%"""
        logger.debug("Запрос на добавление позиции")
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
            logger.debug(f"Разбили запрос stock: {stock}, buy_price: {buy_price}, stock_count: {stock_count}, "
                         f"take_profit: {take_profit}, stop_loss: {stop_loss}")
        except ValueError:
            logger.debug(f"Неправильно введена команда для добавления позиции. User Input: {message.text}")
            await message.answer("Вероятно вы совершили ошибку при написании. Попробуйте указывать цены и проценты "
                                 "через точку.")
            return

        result = self.position_monitor.check_position_pnl(stock=stock, your_buy_price=buy_price,
                                                          stock_count=stock_count,
                                                          growth_threshold=take_profit,
                                                          loss_threshold=stop_loss)
        if result:
            stock_dict = {'ticket': stock, 'buy_price': buy_price, 'count': stock_count, 'take_profit': take_profit,
                          'stop_loss': stop_loss}
            await self.user_repository.add_stock_to_user_by_telegram_id(telegram_id=str(message.chat.id),
                                                                        stock_data=stock_dict)
            logger.debug(f"Успешно добавили {stock} для пользователя {message.chat.id}")
            await message.answer(f"{stock} добавлен в портфель. (Цена покупки: {buy_price}. Кол-во: {stock_count})")
            return
        await message.answer(f"Не удалось найти {stock}")
        logger.debug(f"Не смогли найти {stock} для пользователя {message.chat.id}")

    async def remove_position(self, message: Message):
        logger.debug("Запрос на удаление позиции из портфеля")
        parts = message.text.split()
        if len(parts) < 2:
            logger.debug(f"Пользователь совершил ошибку при вводе (len<2) Исходное сообщение: {message.text}")
            await message.answer("Укажите id позиции. Пример /remove 1")
            return

        try:
            position_id = int(parts[1])
            logger.debug(f"Распарсили команду: position_id: {position_id}")
        except ValueError:
            logger.debug(f"Пользователь ввёл ID не число. Исходное сообщение: {message.text}")
            await message.answer("ID должен быть числом.")
            return

        try:
            await self.user_repository.remove_stock_from_user_by_telegram_id(telegram_id=str(message.chat.id),
                                                                             stock_id=position_id)
            await message.answer(f"Позиция с ID {position_id} успешно удалена")
            logger.debug(f"Успешно удалили позицию {position_id} у пользователя {message.chat.id}")

        except Exception as e:
            await message.answer(f"{str(e)}")
            logger.info(f"Произошла ошибка при удалении у пользователя {message.chat.id} - {str(e)}")
