import asyncio
from aiogram import Dispatcher
from aiogram.client.bot import Bot, DefaultBotProperties
from config import BOT_TOKEN
from bot import router

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
