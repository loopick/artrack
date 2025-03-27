import requests
import asyncio
import sys
from telegram import Bot

# === Твой Telegram-бот ===
TELEGRAM_BOT_TOKEN = "8120670395:AAE7OR2pCgyhG9SqD90H1uZC_T3k5GpZSOs"  # Заменить на свой токен
TELEGRAM_CHAT_ID = "6492452357"  # Твой Telegram ID

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# === API гиперликвидации ===
API_URL = "https://api.hyperliquid.xyz/info"
ADDRESS = "0xf3F496C9486BE5924a93D67e98298733Bb47057c"

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://hypurrscan.io",
    "Referer": "https://hypurrscan.io/",
}

# === Храним предыдущие позиции ===
previous_positions = set()

def get_positions():
    """Запрашивает API и возвращает список активных позиций."""
    try:
        response = requests.post(API_URL, json={"type": "clearinghouseState", "user": ADDRESS}, headers=HEADERS)
        data = response.json()

        # Получаем список активных позиций
        positions = {pos["position"]["coin"] for pos in data.get("assetPositions", [])}
        return positions

    except Exception as e:
        print(f"Ошибка запроса API: {e}")
        return None

async def send_telegram_message(message):
    """Асинхронно отправляет уведомление в Telegram."""
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

async def monitor_positions():
    """Постоянно проверяет API и отправляет уведомления, если позиции изменились."""
    global previous_positions

    while True:
        current_positions = get_positions()
        
        if current_positions is None:
            await asyncio.sleep(60)  # Если API не ответил, пропускаем итерацию
            continue
        
        # Проверяем, есть ли изменения
        if current_positions != previous_positions:
            added = current_positions - previous_positions
            removed = previous_positions - current_positions
            
            message = "🔔 **Обновление позиций трейдера**\n"
            if added:
                message += f"➕ Открыты новые позиции: {', '.join(added)}\n"
            if removed:
                message += f"❌ Закрыты позиции: {', '.join(removed)}\n"
            
            asyncio.create_task(send_telegram_message(message))
            previous_positions = current_positions  # Обновляем состояние

        await asyncio.sleep(60)  # Проверяем раз в минуту

async def main():
    print("✅ Запуск мониторинга...")

    # Запрашиваем начальные позиции
    initial_positions = get_positions()
    
    if initial_positions:
        initial_message = f"🚀 **Бот запущен!**\n🎯 **Текущие позиции:** {', '.join(initial_positions)}"
    else:
        initial_message = "🚀 **Бот запущен!**\n⚠️ **Нет открытых позиций.**"

    await send_telegram_message(initial_message)  # Отправляем сообщение о запуске и позициях
    global previous_positions
    previous_positions = initial_positions  # Устанавливаем стартовые позиции

    try:
        await monitor_positions()  # Запускаем мониторинг
    except Exception as e:
        error_message = f"🚨 **Бот упал!**\nОшибка: {e}"
        await send_telegram_message(error_message)
        sys.exit(1)  # Завершаем скрипт с ошибкой

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Обрабатываем остановку через Ctrl+C
        asyncio.run(send_telegram_message("⚠️ **Бот остановлен вручную!**"))
        print("Бот остановлен вручную.")
    except Exception as e:
        # Обрабатываем любые другие критические ошибки
        asyncio.run(send_telegram_message(f"🚨 **Бот упал!**\nОшибка: {e}"))
        print(f"Критическая ошибка: {e}")
