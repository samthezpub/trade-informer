import datetime
import logging
from datetime import timedelta

import httpx
import requests
from loguru import logger

from core.ports import PriceProvider
from infrastructure.cache.redis_cache import RedisCache


class MoexPriceProvider(PriceProvider):
    def __init__(self, redis_cache: RedisCache):
        self.client = httpx.AsyncClient()
        self.redis_cache = redis_cache

    async def get_current_price(self, stock, date_from=datetime.date.today() - timedelta(days=1),
                                date_to=datetime.date.today(),
                                interval=24):
        """Возвращает последнюю цену закрытия"""
        try:
            cache = await self.redis_cache.get(stock)
            if cache is not None:
                logger.debug(f"Возвращаем закешированный price {cache['price']} для {stock}")
                return cache['price']

            else:
                result = await self.client.get(
                    f'https://iss.moex.com/iss/engines/stock/markets/shares/securities/{stock}/candles.json?from={date_from}&till'
                    f'={date_to}&interval={interval}')
                j = result.json()

                data = [{k: r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']][-1]['close']
                await self.redis_cache.set(stock, {'price': data}, ttl=30)
                return data
        except IndexError as e:
            logger.info(f"get_current_price {e}")
            return None

    async def _get_current_closes(self, stock, hours):
        date_from = datetime.date.today() - timedelta(days=1)  # запас на вчера
        date_to = datetime.date.today()

        result = await self.client.get(
            f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{stock}/candles.json?'
            f'from={date_from}&till={date_to}&interval=60'  # 60 минут
        )

        j = result.json()

        if not j['candles']['data']:
            return None

        # Берём все close за последние N часов
        candles = [{k: r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']]
        closes = [c['close'] for c in candles[-hours:]]  # последние N свечей

        return closes

    async def get_max_price_for_period(self, stock, hours=24):
        """Возвращает максимальную цену закрытия за последние N часов."""

        closes = await self._get_current_closes(stock, hours)
        return max(closes) if closes else None

    async def get_min_price_for_period(self, stock, hours=24):
        """Возвращает минимальную цену закрытия за последние N часов."""
        closes = await self._get_current_closes(stock, hours)

        return min(closes) if closes else None
