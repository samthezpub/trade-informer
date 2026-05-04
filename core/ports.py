from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from infrastructure.database.models import User, Stock


class PriceProvider(ABC):
    @abstractmethod
    def get_current_price(self, stock: str, date_from: datetime, date_to: datetime):
        pass

    @abstractmethod
    def get_max_price_for_period(self, stock: str, hours: int):
        pass

    @abstractmethod
    def get_min_price_for_period(self, stock: str, hours: int):
        pass


class DatabaseManager(ABC):
    @abstractmethod
    async def create_tables(self):
        pass

    @abstractmethod
    async def get_session(self):
        pass

    @abstractmethod
    async def close(self):
        pass


class UserRepository(ABC):
    @abstractmethod
    async def create_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_all_users(self) -> List[User]:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def get_user_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_user_stocks_by_telegram_id(self, telegram_id: str) -> Optional[List[Stock]]:
        pass

    @abstractmethod
    async def add_stock_to_user_by_telegram_id(self, telegram_id: str, stock_data: dict) -> Optional[User]:
        pass

    @abstractmethod
    async def remove_stock_from_user_by_telegram_id(self, telegram_id: str, stock_id: int) -> Optional[User]:
        pass


class CacheProvider(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[dict]:
        pass
    @abstractmethod
    def set(self, key: str, value: dict) -> None:
        pass