class TelegramNotifier:
    def format_position_signal(self, signal_data: dict) -> str:
        pnl = signal_data
        return (f"{pnl['stock']}: Цена {pnl['current_price']}. "
                f"Прибыль {pnl['pnl_pct']}%! Разница {round(pnl['difference'], 2)}Р. Пора фиксировать?")

    def format_report(self, report_data: list) -> str:
        report = report_data
        report_lines = ["📊 <b>Сводный отчёт по позициям</b>\n"]
        total_difference = 0.0

        # Группируем позиции по тикеру, сохраняя порядок первого появления
        grouped = {}
        tickers_order = []  # порядок тикеров, как они встретились в данных

        for pos in report:
            stock = pos.get('stock', '???')
            if stock not in grouped:
                grouped[stock] = {'positions': [], 'total_count': 0, 'total_diff': 0.0}
                tickers_order.append(stock)
            grouped[stock]['positions'].append(pos)
            grouped[stock]['total_count'] += pos.get('count', 0)
            grouped[stock]['total_diff'] += pos.get('difference', 0)

        # Выводим позиции, сгруппированные по тикеру
        for stock in tickers_order:
            data = grouped[stock]
            positions = data['positions']

            # Определяем эмодзи для группы (по худшему сигналу)
            group_emoji = "⚪"
            for pos in positions:
                signal_type = pos.get('type')
                if signal_type == 'STOP_LOSS':
                    group_emoji = "🔴"
                    break
                elif signal_type == 'TAKE_PROFIT':
                    group_emoji = "🟢"

            for pos in positions:
                stock_id = pos.get('stock_id')
                current_price = pos.get('current_price', 0)
                your_price = pos.get('your_price', 0)
                pnl_pct = pos.get('pnl_pct', 0)
                difference = pos.get('difference', 0)
                count = pos.get('count', 0)

                sign = "+" if difference >= 0 else ""

                if stock_id is not None:
                    report_lines.append(f"{group_emoji} <b>{stock}</b> (ID: {stock_id}) ({count} шт.)\n")
                else:
                    report_lines.append(f"{group_emoji} <b>{stock}</b> ({count} шт.)\n")

                report_lines.append(
                    f"   Вход: {your_price:.2f} ₽ → Тек: {current_price:.2f} ₽\n"
                    f"   P&L: {sign}{difference:.2f} ₽ ({sign}{pnl_pct:.2f}%)\n"
                )

                total_difference += difference

            # Итог по группе, если позиций больше одной
            if data['total_count'] > 1:
                total_diff = data['total_diff']
                total_sign = "+" if total_diff >= 0 else ""
                report_lines.append(f"   📌 <b>Итого {stock}: {total_sign}{total_diff:.2f} ₽</b>\n")
            else:
                # Для одиночных позиций можно указать статус
                signal_type = positions[0].get('type')
                if signal_type == 'TAKE_PROFIT':
                    report_lines.append(f"   Статус: Тейк-профит\n")
                elif signal_type == 'STOP_LOSS':
                    report_lines.append(f"   Статус: Стоп-лосс\n")
                else:
                    report_lines.append(f"   Статус: Нейтрально\n")

        # Общий итог
        total_sign = "+" if total_difference >= 0 else ""
        report_lines.append(f"💰 <b>Общий P&L: {total_sign}{total_difference:.2f} ₽</b>")

        return "\n".join(report_lines)
