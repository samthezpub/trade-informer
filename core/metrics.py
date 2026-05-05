# Prometheus metrics
from prometheus_client import Counter
from prometheus_client import Histogram

start_commands = Counter(name="all_users", documentation="Эта метрика показывает сколько всего юзеров "
                                                                   "запустило бота")

# Популярные тикеры (названия акций)
popular_tickers = Histogram(name='popular_tickers', documentation="Популярные тикеры (названия акций)",
                            labelnames=['ticker'])

# Время ответа бота
bot_response_time = Histogram(name='bot_response_time', documentation="Время ответа бота", labelnames=['command'])

# Счётчик для кеша
cache_hits = Counter('cache_hits', 'Количество запрашиваемых цен акций через кеш')
cache_misses = Counter('cache_misses', 'Количество прямых цен запросов акций')