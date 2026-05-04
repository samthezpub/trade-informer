from datetime import datetime

from core.ports import PriceProvider


class MockPriceProvider(PriceProvider):
    async def get_current_price(self, stock: str, date_from: datetime = datetime.now(),
                                date_to: datetime = datetime.now(

                                )) -> float:
        return 100

    async def get_max_price_for_period(self, stock: str, hours: int) -> float:
        return 95

    async def get_min_price_for_period(self, stock: str, hours: int) -> float:
        return 110
