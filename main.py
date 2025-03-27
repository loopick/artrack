from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from bot.telegram_client import TelegramClient
from bot.hyper_api import HyperAPI
from bot.position_monitor import PositionMonitor
from bot.addresses_storage import add_address, remove_address, load_addresses
import asyncio

telegram = TelegramClient()
api = HyperAPI()
monitor = PositionMonitor(api, telegram)

# === Команды ===
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Использование: /add <адрес> [имя]")
        return

    address = context.args[0]
    name = " ".join(context.args[1:]) if len(context.args) > 1 else ""  # Объединяем имя, если оно есть

    add_address(address, name)
    await update.message.reply_text(f"✅ Адрес {address} добавлен как '{name}'")


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажи адрес после команды /remove")
        return
    address = context.args[0]
    if remove_address(address):
        await update.message.reply_text(f"🗑️ Адрес удалён: {address}")
    else:
        await update.message.reply_text(f"⚠️ Адрес не найден: {address}")

async def list_addresses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    addresses = load_addresses()
    if addresses:
        msg = "📜 Отслеживаемые адреса:\n"
        for address, name in addresses.items():
            display_name = f"({name})" if name else ""
            msg += f"🔹 {display_name} https://hypurrscan.io/address/{address}\n"
    else:
        msg = "ℹ️ Пока нет адресов для отслеживания."

    await update.message.reply_text(msg)


# === Старт мониторинга ===
async def on_startup(app):
    addresses = load_addresses()
    if not addresses:
        print("⚠️ ВНИМАНИЕ: В addresses.json НЕТ АДРЕСОВ!")
    asyncio.create_task(monitor.start())

# === Точка входа ===
if __name__ == "__main__":
    app = ApplicationBuilder()\
        .token(telegram.bot.token)\
        .post_init(on_startup)\
        .build()

    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("list", list_addresses))

    print("🤖 Бот готов принимать команды!")
    app.run_polling()
