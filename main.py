from client import StockClient

client = StockClient()
result = client.check_growth('VTBR', growth_threshold=0.5, hours=24)

if result and result['signal']:
    print(result['message'])
else:
    print(f"Текущая цена: {result['current_price']}, просадки нет")

print(client.check_position_pnl('VTBR', 93.91, 8, 0.5, 1))