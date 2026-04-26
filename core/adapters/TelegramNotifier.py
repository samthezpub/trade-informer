class TelegramNotifier:
    def format_position_signal(self, signal_data: dict) -> str:
        pnl = signal_data
        return (f"{pnl['stock']}: Цена {pnl['current_price']}. "
                f"Прибыль {pnl['pnl_pct']}%! Разница {round(pnl['difference'], 2)}Р. Пора фиксировать?")

    def format_report(self, report_data: list) -> str:
        report = report_data
        report_lines = ["📊 <b>Сводный отчёт по позициям</b>\n"]
        total_difference = 0.0

        # Сначала группируем, чтобы посчитать итоги по тикерам
        stock_totals = {}  # { 'VTBR': { 'total_count': 0, 'total_diff': 0.0 } }
        for pos in report:
            stock = pos.get('stock', '???')
            if stock not in stock_totals:
                stock_totals[stock] = {'total_count': 0, 'total_diff': 0.0}
            stock_totals[stock]['total_count'] += pos.get('count', 0)
            stock_totals[stock]['total_diff'] += pos.get('difference', 0)

        # Теперь выводим как раньше, но запоминаем последний тикер
        last_stock = None

        for pos in report:
            stock = pos.get('stock', '???')
            stock_id = pos.get('stock_id')
            current_price = pos.get('current_price', 0)
            your_price = pos.get('your_price', 0)
            pnl_pct = pos.get('pnl_pct', 0)
            difference = pos.get('difference', 0)
            count = pos.get('count', 0)
            signal_type = pos.get('type')

            # Если тикер сменился и у предыдущего была не одна позиция то выводим итог
            if last_stock and last_stock != stock and stock_totals.get(last_stock, {}).get('total_count', 0) > 1:
                total_diff = stock_totals[last_stock]['total_diff']
                total_sign = "+" if total_diff >= 0 else ""
                report_lines.append(f"   📌 <b>Итого {last_stock}: {total_sign}{total_diff:.2f} ₽</b>\n")

            # Определяем эмодзи для типа сигнала
            if signal_type == 'TAKE_PROFIT':
                emoji = "🟢"
                signal_text = "Тейк-профит"
            elif signal_type == 'STOP_LOSS':
                emoji = "🔴"
                signal_text = "Стоп-лосс"
            else:
                emoji = "⚪"
                signal_text = "Нейтрально"

            sign = "+" if difference >= 0 else ""

            if stock_id is not None:
                report_lines.append(f"{emoji} <b>{stock}</b> (ID: {stock_id}) ({count} шт.)\n")
            else:
                report_lines.append(f"{emoji} <b>{stock}</b> ({count} шт.)\n")

            report_lines.append(
                f"   Вход: {your_price:.2f} ₽ → Тек: {current_price:.2f} ₽\n"
                f"   P&L: {sign}{difference:.2f} ₽ ({sign}{pnl_pct:.2f}%)\n"
                f"   Статус: {signal_text}\n"
            )

            total_difference += difference
            last_stock = stock

        # После цикла итог для последнего тикера, если позиций больше одной
        if last_stock and stock_totals.get(last_stock, {}).get('total_count', 0) > 1:
            total_diff = stock_totals[last_stock]['total_diff']
            total_sign = "+" if total_diff >= 0 else ""
            report_lines.append(f"   📌 <b>Итого {last_stock}: {total_sign}{total_diff:.2f} ₽</b>\n")

        total_sign = "+" if total_difference >= 0 else ""
        report_lines.append(f"💰 <b>Общий P&L: {total_sign}{total_difference:.2f} ₽</b>")

        return "\n".join(report_lines)
