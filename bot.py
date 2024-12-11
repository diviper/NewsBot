import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
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
                         "После выбора категории будет показано по 3 новости за раз. "
                         "Используй кнопки 'Предыдущие' и 'Следующие' для переключения между группами новостей.")

@dp.message(Command("refresh"))
async def cmd_refresh(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Технологии", callback_data="tech_news")],
        [InlineKeyboardButton(text="Игровые новости", callback_data="game_news")]
    ])
    await message.answer("Обновляем категории новостей:", reply_markup=keyboard)

def build_keyboard_for_three(news_chunk):
    # news_chunk - список из 1 до 3 новостей
    # Сформируем клавиатуру:
    # Для каждой новости по две кнопки (Читать, Читать здесь)
    # В конце Prev/Next
    rows = []
    for i, news in enumerate(news_chunk, start=1):
        url = news.get("url", "#")
        row = [
            InlineKeyboardButton(text=f"Читать {i}", url=url),
            InlineKeyboardButton(text=f"Читать здесь {i}", web_app=WebAppInfo(url=url))
        ]
        rows.append(row)

    # Кнопки листания
    nav_row = [
        InlineKeyboardButton(text="Предыдущие", callback_data="prev"),
        InlineKeyboardButton(text="Следующие", callback_data="next")
    ]
    rows.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=rows)

async def send_news_chunk(chat_id: int, category: str, index: int):
    all_news = news_data.get((chat_id, category), [])
    if not all_news:
        return

    # Показ по 3 новости
    step = 3
    # Зацикливание
    if index < 0:
        index = len(all_news) - (len(all_news) % step or step)
    elif index >= len(all_news):
        index = 0

    current_index[(chat_id, category)] = index
    chunk = all_news[index:index+3]

    # Формируем текст
    texts = []
    for i, news in enumerate(chunk, start=1):
        title = news.get("title", "Без заголовка")
        date = news.get("date", "")
        parts = [f"{i}) <b>{title}</b>"]
        if date:
            parts.append(f"Дата: {date}")
        texts.append("\n".join(parts))

    full_text = "Список новостей:\n\n" + "\n\n".join(texts)

    kb = build_keyboard_for_three(chunk)

    msg_id = message_ids.get((chat_id, category))
    if msg_id is None:
        sent = await bot.send_message(chat_id=chat_id, text=full_text, parse_mode="HTML", reply_markup=kb)
        message_ids[(chat_id, category)] = sent.message_id
    else:
        await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=full_text, parse_mode="HTML", reply_markup=kb)

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
        await send_news_chunk(chat_id, category, 0)
    else:
        await callback.message.answer("Новостей не найдено.")

@dp.callback_query(lambda c: c.data in ["prev", "next"])
async def pagination_callback(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
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
    step = 3
    if callback.data == "next":
        idx += step
    else:
        idx -= step

    await callback.answer()
    await send_news_chunk(chat_id, active_category, idx)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
