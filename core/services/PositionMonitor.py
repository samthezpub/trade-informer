class PositionMonitor:
    def __init__(self, price_provider):
        self.price_provider = price_provider

    def check_drawdown(self, stock, drop_threshold=0.5, hours=24):
        """Проверяет, упала ли цена на drop_threshold% от максимума за hours часов"""
        current = self.price_provider.get_current_price(stock)
        max_price = self.price_provider.get_max_price_for_period(stock, hours)

        if not max_price or not current:
            return None

        drawdown_pct = (max_price - current) / max_price * 100

        if drawdown_pct >= drop_threshold:
            return {
                'signal': True,
                'current_price': current,
                'max_price': max_price,
                'drawdown_pct': round(drawdown_pct, 2),
                'stock': stock,
            }
        return {'signal': False, 'current_price': current}

    def check_growth(self, stock, growth_threshold=0.5, hours=24):
        """
        Проверяет, выросла ли цена на growth_threshold%
        от МИНИМУМА за последние hours часов.
        """
        current = self.price_provider.get_current_price(stock)
        min_price = self.price_provider.get_min_price_for_period(stock, hours)

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
                'stock': stock,
            }
        return {'signal': False, 'current_price': current}

    def check_position_pnl(self, stock: str, your_buy_price: float, stock_count: int,
                           growth_threshold: float = 0.5,
                           loss_threshold: float = 1.0,
                           stock_id: int = None):
        """
        Проверяет доходность/убыток позиции относительно ВАШЕЙ цены покупки.
        """
        current = self.price_provider.get_current_price(stock)
        if not current:
            return None

        # Считаем процент изменения от вашей цены
        pnl_pct = (current - your_buy_price) / your_buy_price * 100
        difference = (current - your_buy_price) * stock_count

        signal_type = None

        if pnl_pct >= growth_threshold:
            signal_type = 'TAKE_PROFIT'
        elif pnl_pct <= -loss_threshold:
            signal_type = 'STOP_LOSS'

        result = {
            'signal': signal_type is not None,
            'type': signal_type,
            'current_price': current,
            'your_price': your_buy_price,
            'difference': difference,
            'count': stock_count,
            'pnl_pct': round(pnl_pct, 2),
            'stock': stock,
        }
        if stock_id is not None:
            result['stock_id'] = stock_id
        return result
