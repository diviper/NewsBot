import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN
from parsers.tech_parser import get_tech_news
from parsers.game_parser import get_game_news

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилища данных (в памяти)
news_data = {}      # news_data[(chat_id, category)] = список новостей
current_index = {}  # current_index[(chat_id, category)] = текущий индекс новостей

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Технологии", callback_data="tech_news")],
        [InlineKeyboardButton(text="Игровые новости", callback_data="game_news")]
    ])
    await message.answer("Привет! Выбери категорию:", reply_markup=keyboard)

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Команды:\n"
                         "/start - начать выбор категории\n"
                         "/refresh - заново выбрать категорию\n"
                         "После выбора категории можно листать новости по 2 за раз, используя кнопки 'Предыдущие' и 'Следующие'.")

@dp.message(Command("refresh"))
async def cmd_refresh(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Технологии", callback_data="tech_news")],
        [InlineKeyboardButton(text="Игровые новости", callback_data="game_news")]
    ])
    await message.answer("Обновляем категории новостей:", reply_markup=keyboard)

async def show_news_block(message: types.Message, category: str, chat_id: int):
    all_news = news_data.get((chat_id, category), [])
    if not all_news:
        await message.answer("Новостей не найдено.")
        return

    idx = current_index.get((chat_id, category), 0)
    block = all_news[idx:idx+2]

    # Кнопки листания
    control_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Предыдущие", callback_data=f"{category}_prev"),
            InlineKeyboardButton(text="Следующие", callback_data=f"{category}_next")
        ]
    ])

    # Отправляем по 2 новости
    for news in block:
        title = news.get("title", "Без заголовка")
        url = news.get("url", "")
        image = news.get("image", None)
        date = news.get("date", "")
        rating = news.get("likes", None)

        # Формируем текст: Заголовок, Дата, Рейтинг (если есть)
        text_parts = [f"<b>{title}</b>"]
        if date:
            text_parts.append(f"Дата: {date}")
        if rating:
            text_parts.append(f"Рейтинг: {rating}")
        text = "\n".join(text_parts)

        link_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Читать", url=url)]
        ])

        if image:
            await message.answer_photo(photo=image, caption=text, parse_mode="HTML", reply_markup=link_keyboard)
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=link_keyboard)

    await message.answer("Листайте новости:", reply_markup=control_keyboard)

@dp.callback_query(lambda c: c.data in ["tech_news", "game_news"])
async def category_callback(callback: types.CallbackQuery):
    category = "tech" if callback.data == "tech_news" else "game"
    chat_id = callback.message.chat.id

    if category == "tech":
        all_news = get_tech_news()
    else:
        all_news = get_game_news()

    news_data[(chat_id, category)] = all_news
    current_index[(chat_id, category)] = 0

    await callback.answer()
    await show_news_block(callback.message, category, chat_id)

@dp.callback_query(lambda c: c.data.endswith("_prev") or c.data.endswith("_next"))
async def pagination_callback(callback: types.CallbackQuery):
    data = callback.data
    parts = data.split("_")
    category = parts[0]
    direction = parts[1]
    chat_id = callback.message.chat.id

    all_news = news_data.get((chat_id, category), [])
    if not all_news:
        await callback.message.answer("Новостей не найдено.")
        await callback.answer()
        return

    idx = current_index.get((chat_id, category), 0)
    step = 2

    if direction == "next":
        idx += step
        if idx >= len(all_news):
            idx = 0
    else:  # prev
        idx -= step
        if idx < 0:
            # Переход к концу списка по 2 элемента:
            # idx должен сдвинуться так, чтобы показывать последний блок из 2 новостей
            remainder = len(all_news) % step
            if remainder == 0:
                idx = len(all_news) - step
            else:
                idx = len(all_news) - remainder

    current_index[(chat_id, category)] = idx

    await callback.answer()
    await show_news_block(callback.message, category, chat_id)
