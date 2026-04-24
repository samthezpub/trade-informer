class TelegramNotifier:
    def format_position_signal(self, signal_data:dict) -> str:
        pnl = signal_data
        return (f"{pnl['stock']}: Цена {pnl['current_price']}. "
                f"Прибыль {pnl['pnl_pct']}%! Разница {round(pnl['difference'], 2)}Р. Пора фиксировать?")
