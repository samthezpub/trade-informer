import datetime
from datetime import timedelta

import requests


# TODO Рефактор в сервис + репо
class StockClient:
    def __init__(self):
        pass

    def get_current_price(self, stock, date_from=datetime.date.today() - timedelta(days=1),
                          date_to=datetime.date.today(),
                          interval=24):
        """Возвращает последнюю цену закрытия"""
        j = requests.get(
            f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{stock}/candles.json?from={date_from}&till'
            f'={date_to}&interval={interval}').json()

        data = [{k: r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']][-1]['close']
        return data

    def get_max_price_for_period(self, stock, hours=24):
        """Возвращает максимальную цену закрытия за последние N часов."""
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

        return max(closes) if closes else None

    def get_min_price_for_period(self, stock, hours=24):
        """Возвращает минимальную цену закрытия за последние N часов."""
        date_from = datetime.date.today() - timedelta(days=1)
        date_to = datetime.date.today()

        j = requests.get(
            f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{stock}/candles.json?'
            f'from={date_from}&till={date_to}&interval=60'
        ).json()

        if not j['candles']['data']:
            return None

        candles = [{k: r[i] for i, k in enumerate(j['candles']['columns'])} for r in j['candles']['data']]
        closes = [c['close'] for c in candles[-hours:]]

        return min(closes) if closes else None

    def check_drawdown(self, stock, drop_threshold=0.5, hours=24):
        """Проверяет, упала ли цена на drop_threshold% от максимума за hours часов"""
        current = self.get_current_price(stock)
        max_price = self.get_max_price_for_period(stock, hours)

        if not max_price or not current:
            return None

        drawdown_pct = (max_price - current) / max_price * 100

        if drawdown_pct >= drop_threshold:
            return {
                'signal': True,
                'current_price': current,
                'max_price': max_price,
                'drawdown_pct': round(drawdown_pct, 2),
                'message': f'ВТБ: просадка {round(drawdown_pct, 2)}% от {max_price} до {current}'
            }
        return {'signal': False, 'current_price': current}

    def check_growth(self, stock, growth_threshold=0.5, hours=24):
        """
        Проверяет, выросла ли цена на growth_threshold%
        от МИНИМУМА за последние hours часов.
        """
        current = self.get_current_price(stock)
        min_price = self.get_min_price_for_period(stock, hours)

        if not min_price or not current:
            return None

        # Считаем процент РОСТА от минимума
        growth_pct = (current - min_price) / min_price * 100

        if growth_pct >= growth_threshold:
            return {
                'signal': True,
                'current_price': current,
                'min_price': min_price,
                'growth_pct': round(growth_pct, 2),
                'message': f'ВТБ: рост {round(growth_pct, 2)}% от {min_price} до {current}'
            }
        return {'signal': False, 'current_price': current}

    def check_position_pnl(self, stock, your_buy_price, stock_count, growth_threshold=0.5, loss_threshold=1.0):
        """
        Проверяет доходность/убыток позиции относительно ВАШЕЙ цены покупки.
        """
        current = self.get_current_price(stock)
        if not current:
            return None

        # Считаем процент изменения от вашей цены
        pnl_pct = (current - your_buy_price) / your_buy_price * 100
        difference = (current - your_buy_price) * stock_count

        signal_type = None
        message = None

        if pnl_pct >= growth_threshold:
            signal_type = 'TAKE_PROFIT'
            message = (f'{stock}: Цена {current}. Прибыль {round(pnl_pct, 2)}%! Разница '
                       f'{round(difference, 2)}Р. Пора фиксировать?')
        elif pnl_pct <= -loss_threshold:
            signal_type = 'STOP_LOSS'
            message = (f'{stock}: Цена {current}. Убыток {round(abs(pnl_pct), 2)}%! Разница '
                       f'{round(difference, 2)}Р.  Пора закрывать?')

        return {
            'signal': signal_type is not None,
            'type': signal_type,
            'current_price': current,
            'your_price': your_buy_price,
            'difference': difference,
            'count': stock_count,
            'pnl_pct': round(pnl_pct, 2),
            'message': message
        }
