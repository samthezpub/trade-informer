from datetime import datetime, timedelta
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from loguru import logger


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для защиты от спама (Rate Limiting) на основе скользящего окна"""

    def __init__(self, time_for_update_limit: int = 60, requests_per_limit: int = 5):
        self.requests = {}
        self._time_for_update_limit = time_for_update_limit
        self._requests_per_limit = requests_per_limit

    def _add_user_request(self, user_id: int, request, timestamp):
        # Если пользователя нет в словаре добавляем его ключ и пустой массив
        if user_id not in self.requests:
            self.requests[user_id] = []
        # Добавляем время выполнения запроса
        self.requests[user_id].append(timestamp)

    def _remove_expired_requests(self, user_id):
        if user_id in self.requests:
            for request_date in self.requests[user_id]:
                # Удаляем если дата запроса уже соответствует лимиту
                if request_date <= datetime.now() - timedelta(seconds=self._time_for_update_limit):
                    self.requests[user_id].remove(request_date)

    def _check_user_request(self, user_id: int, timestamp: datetime) -> bool:
        # Проверяем количество записей в списке, определяя вышли ли за лимит
        if len(self.requests[user_id]) > self._requests_per_limit:
            logger.debug(f"Пользователь {user_id} имеет {self.requests[user_id]} запросов, блокируем запрос")
            return True
        return False

    async def __call__(self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: dict[str, Any]) -> Any:
        user_id = event.from_user.id
        timestamp = datetime.now()
        self._add_user_request(user_id, event, timestamp)
        self._remove_expired_requests(user_id)
        is_limit_reached = self._check_user_request(user_id, timestamp)
        if is_limit_reached:
            await event.answer(f"Слишком много запросов, попробуйте через {self._time_for_update_limit} секунд.")
            return
        return await handler(event, data)
