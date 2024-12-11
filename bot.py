from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
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
    await message.answer("Используй /start или /refresh, чтобы выбрать категорию новостей.")

@router.message(Command("refresh"))
async def cmd_refresh(message: types.Message):
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

            # Используем web_app для открытия ссылки в мини-приложении (WebApp)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Читать", web_app=WebAppInfo(url=url))]
            ])

            if image:
                caption = title
                # Добавим рейтинг в подпись, если он есть:
                rating = news.get("likes", "0")
                if rating and rating != "0":
                    caption = f"{title}\nРейтинг: {rating}"
                await callback.message.answer_photo(photo=image, caption=caption, reply_markup=keyboard)
            else:
                # Если нет картинки, отправим просто текст с рейтингом, если он не ноль
                rating = news.get("likes", "0")
                if rating and rating != "0":
                    text = f"{title}\nРейтинг: {rating}"
                else:
                    text = title
                await callback.message.answer(text=text, reply_markup=keyboard)

    await callback.answer()
