from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ParseMode
from fastapi import FastAPI, Request
import uvicorn
import asyncio

API_TOKEN = "7292839933:AAGpBvKyDZGdFotJDwVKelwXmjk6HQN_Ui4"
CHANNEL_ID = "-1002769883348"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = FastAPI()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("👋 Привет! Я бот Alpha Enters. Готов к работе.")

@dp.message_handler(commands=['signal'])
async def handle_signal(message: types.Message):
    text = message.get_args()
    if not text:
        await message.reply("⚠️ Используй так: /signal ваш_текст_сигнала")
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

if __name__ == '__main__':
    import threading

    def run_fastapi():
        uvicorn.run(app, host="0.0.0.0", port=8000)

    threading.Thread(target=run_fastapi).start()
    executor.start_polling(dp, skip_updates=True)
