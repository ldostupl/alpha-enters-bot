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
    args = message.get_args().lower().split()

    try:
        direction = args[0].upper()
        asset = args[1].upper()

        entry = None
        sl = None
        tps = []

        i = 2
        while i < len(args):
            if args[i] == "entry":
                entry = args[i + 1]
                i += 2
            elif args[i] == "tp":
                i += 1
                while i < len(args) and args[i].replace('.', '', 1).isdigit():
                    tps.append(args[i])
                    i += 1
            elif args[i].startswith("sl"):
                sl = args[i].replace("sl", "")
                if not sl:
                    sl = args[i + 1]
                    i += 2
                else:
                    i += 1
            else:
                i += 1

        if not all([direction, asset, entry, sl, tps]):
            raise ValueError("⚠️ Не хватает обязательных параметров")

        # 🧾 Формируем текст
        msg = f"""📢 *Новый сигнал от Alpha Enters*:

🔸 Вход: {direction}
💰 Актив: {asset}
📥 Entry: {entry}"""

        for idx, tp in enumerate(tps, 1):
            msg += f"\n🎯 TP{idx}: {tp}"

        msg += f"\n🛡️ SL: {sl}"

        await bot.send_message(CHANNEL_ID, msg, parse_mode=ParseMode.MARKDOWN)
        await message.reply("✅ Сигнал отправлен в канал")

    except Exception as e:
        print(e)
        await message.reply("❌ Ошибка: убедитесь в правильности команды. Пример:\n/signal long btc entry 61200 tp 61800 62300 62900 sl 60400")



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
