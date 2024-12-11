import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, WebAppInfo
from config import BOT_TOKEN
from parsers.tech_parser import get_tech_news
from parsers.game_parser import get_game_news

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

news_data = {}
current_index = {}
message_ids = {}
default_image = "https://via.placeholder.com/600x400?text=No+Image"

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
                         "/refresh - заново выбрать категорию\n\n"
                         "После выбора категории будет показана одна новость. "
                         "Используй кнопки 'Предыдущие' и 'Следующие' для переключения между новостями.")

@dp.message(Command("refresh"))
async def cmd_refresh(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Технологии", callback_data="tech_news")],
        [InlineKeyboardButton(text="Игровые новости", callback_data="game_news")]
    ])
    await message.answer("Обновляем категории новостей:", reply_markup=keyboard)

def build_keyboard(url: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Читать", url=url),
         InlineKeyboardButton(text="Читать здесь", web_app=WebAppInfo(url=url))],
        [InlineKeyboardButton(text="Предыдущие", callback_data="prev"),
         InlineKeyboardButton(text="Следующие", callback_data="next")]
    ])

async def send_news(chat_id: int, category: str, index: int):
    all_news = news_data.get((chat_id, category), [])
    if not all_news:
        return

    # Зацикливание
    if index < 0:
        index = len(all_news) - 1
    elif index >= len(all_news):
        index = 0

    current_index[(chat_id, category)] = index
    news = all_news[index]

    title = news.get("title", "Без заголовка")
    url = news.get("url", "#")
    date = news.get("date", "")
    rating = news.get("likes", None)
    image = news.get("image", None) or default_image

    parts = [f"<b>{title}</b>"]
    if date:
        parts.append(f"Дата: {date}")
    if rating:
        parts.append(f"Рейтинг: {rating}")
    caption = "\n".join(parts)

    kb = build_keyboard(url)

    msg_id = message_ids.get((chat_id, category), None)
    if msg_id is None:
        # Отправляем новое сообщение
        sent = await bot.send_photo(chat_id=chat_id, photo=image, caption=caption, parse_mode="HTML", reply_markup=kb)
        message_ids[(chat_id, category)] = sent.message_id
    else:
        # Редактируем существующее
        media = InputMediaPhoto(media=image, caption=caption, parse_mode="HTML")
        await bot.edit_message_media(chat_id=chat_id, message_id=msg_id, media=media, reply_markup=kb)

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
    message_ids.pop((chat_id, category), None)

    await callback.answer()

    if all_news:
        await send_news(chat_id, category, 0)
    else:
        await callback.message.answer("Новостей не найдено.")

@dp.callback_query(lambda c: c.data in ["prev", "next"])
async def pagination_callback(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    # Определяем категорию
    possible_categories = ["tech", "game"]
    active_category = None
    for cat in possible_categories:
        if (chat_id, cat) in news_data and news_data[(chat_id, cat)]:
            active_category = cat
            break

    if not active_category:
        await callback.answer("Категория не определена.")
        return

    idx = current_index.get((chat_id, active_category), 0)
    if callback.data == "next":
        idx += 1
    else:
        idx -= 1

    await callback.answer()
    await send_news(chat_id, active_category, idx)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
