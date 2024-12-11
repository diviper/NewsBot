# bot.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="AI новости", callback_data="ai_news")],
        [InlineKeyboardButton(text="Игровые новости", callback_data="game_news")]
    ])
    await message.answer("Привет! Выбери категорию:", reply_markup=keyboard)

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Используй /start, чтобы начать. Выбери категорию новостей. Нажми на нужную кнопку, чтобы увидеть последние новости.")

@router.callback_query(lambda c: c.data in ["ai_news", "game_news"])
async def news_callback(callback: types.CallbackQuery):
    # Здесь логика получения новостей. В зависимости от callback_data вызовем парсер:
    from parsers.ai_parser import get_ai_news
    from parsers.game_parser import get_game_news
    from formatters import format_news_list
    
    if callback.data == "ai_news":
        news_list = get_ai_news()
    else:
        news_list = get_game_news()

    # Форматируем и отправляем ответ
    if news_list:
        text = format_news_list(news_list)
    else:
        text = "Новостей не найдено."
    
    await callback.message.answer(text)
    await callback.answer()
