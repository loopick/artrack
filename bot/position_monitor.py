import asyncio
from bot.addresses_storage import load_addresses

class PositionMonitor:
    def __init__(self, api_client, telegram_client):
        self.api = api_client
        self.telegram = telegram_client
        self.previous_positions = {}

    async def start(self):
        """Запускает мониторинг для всех адресов из JSON"""
        addresses = load_addresses()
        if not addresses:
            print("⚠️ Нет адресов для мониторинга.")
            return

        for address, name in addresses.items():
            positions = self.api.get_positions(address)
            self.previous_positions[address] = positions or set()

            display_name = f"👤 {name}" if name else "Без имени"
            url = f"https://hypurrscan.io/address/{address}"
            msg = f"🚀 Бот запущен для\n{display_name}\n{url}\n"
            if positions:
                msg += f"🎯 Текущие позиции: {', '.join(positions)}"
            else:
                msg += "⚠️ Нет открытых позиций."

            await self.telegram.send_message(msg)

        if not hasattr(self, "monitoring_task") or self.monitoring_task.done():
            self.monitoring_task = asyncio.create_task(self.monitor_loop())  # 👈 Запускаем только один раз!

    async def monitor_loop(self):
        """Цикл мониторинга адресов"""
        while True:
            addresses = load_addresses()
            for address, name in addresses.items():
                current_positions = self.api.get_positions(address)

                if current_positions is None:
                    continue

                prev_positions = self.previous_positions.get(address, set())
                if current_positions != prev_positions:
                    added = current_positions - prev_positions
                    removed = prev_positions - current_positions

                    message = f"🔔 **Обновление позиций для {name}**\n"
                    if added:
                        message += f"➕ Открыты новые позиции: {', '.join(added)}\n"
                    if removed:
                        message += f"❌ Закрыты позиции: {', '.join(removed)}\n"

                    asyncio.create_task(self.telegram.send_message(message))
                    self.previous_positions[address] = current_positions

            await asyncio.sleep(60)  # Проверяем раз в 5 секунд
