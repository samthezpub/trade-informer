class TelegramNotifier:
    def format_position_signal(self, signal_data:dict) -> str:
        pnl = signal_data
        return (f"{pnl['stock']}: Цена {pnl['current_price']}. "
                f"Прибыль {pnl['pnl_pct']}%! Разница {round(pnl['difference'], 2)}Р. Пора фиксировать?")

    def format_report(self, report_data:list) -> str:
        report = report_data
        # Формируем красивое сообщение
        report_lines = ["📊 <b>Сводный отчёт по позициям</b>\n"]

        total_difference = 0  # Общий P&L

        for pos in report:
            stock = pos['stock']
            current_price = pos['current_price']
            your_price = pos['your_price']
            pnl_pct = pos['pnl_pct']
            difference = pos['difference']
            count = pos['count']
            signal_type = pos['type']

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

            # Добавляем блок по каждой позиции
            report_lines.append(
                f"{emoji} <b>{stock}</b> ({count} шт.)\n"
                f"   Вход: {your_price:.2f} ₽ → Тек: {current_price:.2f} ₽\n"
                f"   P&L: {sign}{difference:.2f} ₽ ({sign}{pnl_pct:.2f}%)\n"
                f"   Статус: {signal_text}\n"
            )

            total_difference += difference

        # Добавляем итоговую строку
        total_sign = "+" if total_difference >= 0 else ""
        report_lines.append(f"💰 <b>Общий P&L: {total_sign}{total_difference:.2f} ₽</b>")

        return "\n".join(report_lines)