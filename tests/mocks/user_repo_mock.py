from typing import Optional, List

from core.ports import UserRepository
from infrastructure.database.models import User, Stock


class UserRepositoryMock(UserRepository):
    def __init__(self):
        self._users = {}       # {telegram_id: User}
        self._stocks = {}      # {stock_id: Stock}
        self._next_user_id = 1
        self._next_stock_id = 1

    async def create_user(self, user) -> None:
        user.id = self._next_user_id
        self._next_user_id += 1
        self._users[user.telegram_id] = user

    async def get_all_users(self) -> List:
        return list(self._users.values())

    async def get_user_by_id(self, user_id: int):
        for user in self._users.values():
            if user.id == user_id:
                return user
        return None

    async def get_user_by_telegram_id(self, telegram_id: str):
        return self._users.get(telegram_id)

    async def get_user_stocks_by_telegram_id(self, telegram_id: str) -> Optional[List]:
        user = self._users.get(telegram_id)
        if user:
            return [s for s in self._stocks.values() if s.user_id == user.id]
        return None

    async def add_stock_to_user_by_telegram_id(self, telegram_id: str, stock_data: dict):
        user = self._users.get(telegram_id)
        if not user:
            raise Exception(f"Пользователь с telegram_id {telegram_id} не найден.")

        stock = type('Stock', (), {})()
        for key, value in stock_data.items():
            setattr(stock, key, value)
        stock.id = self._next_stock_id
        stock.user_id = user.id
        self._next_stock_id += 1

        self._stocks[stock.id] = stock
        return user

    async def remove_stock_from_user_by_telegram_id(self, telegram_id: str, stock_id: int):
        stock = self._stocks.get(stock_id)
        if not stock:
            raise Exception(f"Позиция с ID {stock_id} не найдена.")


        user = self._users.get(telegram_id)
        if not user or stock.user_id != user.id:
            raise Exception(f"Позиция с ID {stock_id} не принадлежит вам.")
        del self._stocks[stock_id]
