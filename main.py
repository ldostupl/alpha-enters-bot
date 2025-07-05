from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ParseMode
from fastapi import FastAPI, Request
import uvicorn
import os
import threading
import asyncio

# ✅ Получаем переменные окружения
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# 🔐 Проверяем, что токен и ID канала заданы
if not API_TOKEN or not CHANNEL_ID:
    raise ValueError("❌ API_TOKEN или CHANNEL_ID не заданы в переменных окружения!")

# 🔧 Инициализация бота и FastAPI
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = FastAPI()

# 🧾 Обработка команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("👋 Привет! Бот Alpha Enters работает.\nИспользуй /signal чтобы отправить сигнал в канал.")

# 📩 Обработка команды /signal
@dp.message_handler(commands=['signal'])
async def handle_signal(message: types.Message):
    text = message.get_args()
    if not text:
        await message.reply("⚠️ Пример: /signal Вход LONG по BTC с TP и SL")
        return
    await bot.send_message(CHANNEL_ID, text, parse_mode=ParseMode.MARKDOWN)
    await message.reply("✅ Сигнал отправлен в канал")

# 🔗 Webhook для TradingView или других систем
@app.post("/webhook")
async def webhook_tv(request: Request):
    data = await request.json()
    print(f"📩 Webhook received: {data}")  # лог для отладки
    msg = data.get("message")
    if msg:
        asyncio.create_task(bot.send_message(CHANNEL_ID, msg, parse_mode=ParseMode.MARKDOWN))
        return {"status": "sent"}
    return {"status": "no_message"}

# 🌐 Запускаем FastAPI в отдельном потоке
def start():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 🚀 Запуск
if __name__ == '__main__':
    threading.Thread(target=start).start()
    executor.start_polling(dp, skip_updates=True)
