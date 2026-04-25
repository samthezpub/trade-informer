class TelegramNotifier:
    def format_position_signal(self, signal_data: dict) -> str:
        pnl = signal_data
        return (f"{pnl['stock']}: Цена {pnl['current_price']}. "
                f"Прибыль {pnl['pnl_pct']}%! Разница {round(pnl['difference'], 2)}Р. Пора фиксировать?")

    def format_report(self, report_data: list) -> str:
        report = report_data
        # Формируем красивое сообщение
        report_lines = ["📊 <b>Сводный отчёт по позициям</b>\n"]

        total_difference = 0  # Общий P&L

        for pos in report:
            stock = pos.get('stock', '???')
            stock_id = pos.get('stock_id')
            current_price = pos.get('current_price', 0)
            your_price = pos.get('your_price', 0)
            pnl_pct = pos.get('pnl_pct', 0)
            difference = pos.get('difference', 0)
            count = pos.get('count', 0)
            signal_type = pos.get('type')

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

            # Определяем знак для разницы
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

        # Добавляем итоговую строку
        total_sign = "+" if total_difference >= 0 else ""
        report_lines.append(f"💰 <b>Общий P&L: {total_sign}{total_difference:.2f} ₽</b>")

        return "\n".join(report_lines)
