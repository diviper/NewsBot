from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from parsers.ai_parser import get_ai_news
from parsers.game_parser import get_game_news

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
    await message.answer("Используй /start, чтобы начать. Нажми на нужную кнопку, чтобы увидеть последние новости.\n"
                         "Используй /refresh, чтобы снова выбрать категорию новостей.")

@router.message(Command("refresh"))
async def cmd_refresh(message: types.Message):
    # Повторяем логику из /start
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="AI новости", callback_data="ai_news")],
        [InlineKeyboardButton(text="Игровые новости", callback_data="game_news")]
    ])
    await message.answer("Обновляем категории новостей:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data in ["ai_news", "game_news"])
async def news_callback(callback: types.CallbackQuery):
    if callback.data == "ai_news":
        news_list = get_ai_news()
    else:
        news_list = get_game_news()

    if not news_list:
        await callback.message.answer("Новостей не найдено.")
    else:
        for news in news_list:
            title = news.get("title", "Без заголовка")
            url = news.get("url", "")
            image = news.get("image", None)
            
            # Создаем кнопку для перехода по ссылке
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Читать", url=url)]
            ])
            
            if image:
                # Отправляем фото с заголовком и кнопкой
                await callback.message.answer_photo(photo=image, caption=title, reply_markup=keyboard)
            else:
                # Отправляем просто заголовок и кнопку
                await callback.message.answer(text=title, reply_markup=keyboard)

    await callback.answer()
