import asyncio

from aiogram import Bot
from aiogram.enums import ParseMode
from loguru import logger

from core.adapters.TelegramNotifier import TelegramNotifier
from core.services.PositionMonitor import PositionMonitor
from infrastructure.repositories.user_repo import SQLAlchemyUserRepository


class ReportScheduler:
    def __init__(self, bot: Bot, monitor: PositionMonitor, notifier: TelegramNotifier,
                 user_repo: SQLAlchemyUserRepository,
                 interval_seconds:
                 int = 300):
        self.bot = bot
        self.monitor = monitor
        self.notifier = notifier
        self.user_repo = user_repo
        self.interval = interval_seconds
        self._task = None

    async def start(self):
        """Запускает фоновую задачу рассылки."""
        self._task = asyncio.create_task(self._run())
        logger.debug("Задача рассылки запущена")

    async def _run(self):
        """Основной цикл рассылки."""
        await asyncio.sleep(5)  # даём боту время запуститься
        while True:
            try:
                await self._send_scheduled_reports()
            except Exception as e:
                logger.error(f"Ошибка в scheduled report: {e}")
            await asyncio.sleep(self.interval)

    async def _send_scheduled_reports(self):
        """Генерирует и отправляет отчёты всем пользователям, у которых есть позиции."""
        # Получаем все уникальные telegram_id из БД
        users = await self.user_repo.get_all_users()
        logger.debug("Пользователи для рассылки получены {users}".format(users=len(users)))

        for user in users:
            try:
                # Получаем позиции пользователя
                positions = await self.user_repo.get_user_stocks_by_telegram_id(telegram_id=str(user.telegram_id))
                if not positions:
                    logger.debug(f"У пользователя {user} нет позиций")
                    continue
                logger.debug(f"Получили позиции пользователя {user} {positions}")
                results = []
                for pos in positions:
                    result = self.monitor.check_position_pnl(
                        stock=pos.ticket,
                        your_buy_price=pos.buy_price,
                        stock_count=pos.count,
                        growth_threshold=pos.take_profit,
                        loss_threshold=pos.stop_loss
                    )
                    if result:
                        result['stock'] = pos.ticket
                        result['count'] = pos.count
                        results.append(result)
                        logger.info(f"Нет результата по позиции {pos}, рекомендуется проверить, result: {result}")

                # Отправляем отчёт
                if results:
                    msg = self.notifier.format_report(results)
                    await self.bot.send_message(int(user.telegram_id), msg, parse_mode=ParseMode.HTML)
                    logger.debug(f"Отправили отчёт пользователю {user.telegram_id}")

            except Exception as e:
                logger.info(f"Ошибка отправки отчёта пользователю {user.telegram_id}: {e}")
                continue
