from abc import ABC, abstractmethod
from datetime import datetime


class PriceProvider(ABC):
    @abstractmethod
    def get_current_price(self, stock:str, date_from:datetime, date_to:datetime):
        pass

    @abstractmethod
    def get_max_price_for_period(self, stock:str, hours:int):
        pass

    @abstractmethod
    def get_min_price_for_period(self, stock:str, hours:int):
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
