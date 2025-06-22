from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ParseMode
from fastapi import FastAPI, Request
import uvicorn
import os
import threading

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

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
        await message.reply("⚠️ Пример: /signal Вход LONG по BTC с TP и SL")
        return
    await bot.send_message(CHANNEL_ID, text, parse_mode=ParseMode.MARKDOWN)
    await message.reply("✅ Сигнал отправлен в канал")


@app.post("/webhook")
async def webhook_tv(request: Request):
    data = await request.json()
    msg = data.get("message")
    if msg:
        await bot.send_message(CHANNEL_ID, msg, parse_mode=ParseMode.MARKDOWN)
        return {"status": "sent"}
    return {"status": "no_message"}


def start():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    threading.Thread(target=start).start()
    executor.start_polling(dp, skip_updates=True)
