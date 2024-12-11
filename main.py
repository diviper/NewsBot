# main.py
import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from bot import router

async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)

    # Удаляем старые апдейты и запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
