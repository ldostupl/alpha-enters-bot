from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from fastapi import FastAPI, Request
import uvicorn
import os
import asyncio

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not API_TOKEN or not CHANNEL_ID:
    raise ValueError("API_TOKEN или CHANNEL_ID не заданы!")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = FastAPI()


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("👋 Привет! Бот Alpha Enters работает.\nИспользуй /signal чтобы отправить сигнал в канал.")


@dp.message_handler(commands=['signal'])
async def handle_signal(message: types.Message):
    args = message.get_args()
    if not args:
        await message.reply("⚠️ Пример: /signal LONG BTC 61200 62800 60400")
        return

    try:
        position, pair, entry, target, stop = args.split()
        formatted = (
            f"🚀 [{position.upper()}] {pair.upper()} от {entry}\n"
            f"🎯 Цель: {target}\n"
            f"🛑 Стоп: {stop}\n"
            f"📊 Риск/прибыль: ?\n"
            f"📅 Время: {message.date.strftime('%d.%m.%Y %H:%M')}"
        )
    except ValueError:
        formatted = args  # если не по шаблону — шлём как есть

    await bot.send_message(CHANNEL_ID, formatted, parse_mode=ParseMode.MARKDOWN)
    await message.reply("✅ Сигнал отправлен в канал")


@app.post("/webhook")
async def webhook_tv(request: Request):
    data = await request.json()
    msg = data.get("message")
    if msg:
        asyncio.create_task(bot.send_message(CHANNEL_ID, msg, parse_mode=ParseMode.MARKDOWN))
        return {"status": "sent"}
    return {"status": "no_message"}


# 👇 Асинхронный запуск и FastAPI, и бота
async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(uvicorn.run(app, host="0.0.0.0", port=8000))
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
