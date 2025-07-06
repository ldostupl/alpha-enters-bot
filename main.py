from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from fastapi import FastAPI, Request
from uvicorn import Config, Server
import uvicorn
import os
import asyncio

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not API_TOKEN or not CHANNEL_ID:
    raise ValueError("❌ API_TOKEN или CHANNEL_ID не заданы в переменных окружения!")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = FastAPI()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("👋 Привет! Бот Alpha Enters работает.\nИспользуй /signal чтобы отправить сигнал в канал.")


@dp.message_handler(commands=['signal'])
async def handle_signal(message: types.Message):
    text = message.get_args()
    if not text:
        await message.reply("⚠️ Пример: /signal long btc entry 61200 tp 61800 62300 62900 sl 60400")
        return

    try:
        parts = text.lower().split()
        direction = parts[0].upper()         # long
        asset = parts[1].upper()             # btc
        entry_price = parts[parts.index("entry") + 1]
        tp_index = parts.index("tp")
        sl_index = parts.index("sl")
        tps = parts[tp_index + 1:sl_index]   # [61800, 62300, 62900]
        sl_price = parts[sl_index + 1]

        tp_text = " / ".join(tps)

        formatted = (
            f"📢 *Новый сигнал от Alpha Enters*:\n\n"
            f"🔸 Вход: {direction}\n"
            f"💰 Актив: {asset}\n"
            f"🎯 TP: {tp_text}\n"
            f"🛡️ SL: {sl_price}"
        )
        await bot.send_message(CHANNEL_ID, formatted, parse_mode=ParseMode.MARKDOWN)
        await message.reply("✅ Сигнал отправлен в канал")

    except Exception as e:
        await message.reply(f"❌ Ошибка обработки сигнала: {e}")



@app.post("/webhook")
async def webhook_tv(request: Request):
    data = await request.json()
    msg = data.get("message")
    if msg:
        asyncio.create_task(bot.send_message(CHANNEL_ID, msg, parse_mode=ParseMode.MARKDOWN))
        return {"status": "sent"}
    return {"status": "no_message"}


async def main():
    # 🔄 Запускаем FastAPI сервер
    config = Config(app=app, host="0.0.0.0", port=8000, log_level="info")
    server = Server(config)

    # 🔃 Создаём задачу на запуск сервера
    loop = asyncio.get_running_loop()
    loop.create_task(server.serve())

    # ▶️ Запускаем aiogram
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
