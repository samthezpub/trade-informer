from core.adapters.MoexPriceProvider import MoexPriceProvider
from core.services.PositionMonitor import PositionMonitor
from core.adapters.TelegramNotifier import TelegramNotifier

price_provider = MoexPriceProvider()
monitor = PositionMonitor(price_provider)
notifier = TelegramNotifier()

result = monitor.check_position_pnl('VTBR', 93.00, 8, 0.5, 1)
print(result)
if result['signal']:
    message = notifier.format_position_signal(result)
    print(message)
