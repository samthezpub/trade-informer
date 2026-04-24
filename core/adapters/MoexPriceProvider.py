import datetime
from datetime import timedelta
import requests
from core.ports import PriceProvider


class MoexPriceProvider(PriceProvider):

    def get_current_price(self, stock, date_from=datetime.date.today() - timedelta(days=1),
                          date_to=datetime.date.today(),
                          interval=24):
        """Возвращает последнюю цену закрытия"""
        j = requests.get(
            f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{stock}/candles.json?from={date_from}&till'
            f'={date_to}&interval={interval}').json()

        data = [{k: r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']][-1]['close']
        return data

    def _get_current_closes(self, stock, hours):
        date_from = datetime.date.today() - timedelta(days=1)  # запас на вчера
        date_to = datetime.date.today()

        j = requests.get(
            f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{stock}/candles.json?'
            f'from={date_from}&till={date_to}&interval=60'  # 60 минут
        ).json()

        if not j['candles']['data']:
            return None

        # Берём все close за последние N часов
        candles = [{k: r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']]
        closes = [c['close'] for c in candles[-hours:]]  # последние N свечей

        return closes

    def get_max_price_for_period(self, stock, hours=24):
        """Возвращает максимальную цену закрытия за последние N часов."""

        closes = self._get_current_closes(stock, hours)
        return max(closes) if closes else None

    def get_min_price_for_period(self, stock, hours=24):
        """Возвращает минимальную цену закрытия за последние N часов."""
        closes = self._get_current_closes(stock, hours)

        return min(closes) if closes else None


