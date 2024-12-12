import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, WebAppInfo
from config import BOT_TOKEN
from parsers.tech_parser import get_tech_news
from parsers.game_parser import get_game_news

# Настройка логирования
logging.basicConfig(
    filename="debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

news_data = {}
current_index = {}
default_image = "https://via.placeholder.com/600x400?text=No+Image"

# Главное меню
def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Технологии", callback_data="tech_news")],
        [InlineKeyboardButton(text="Игровые новости", callback_data="game_news")]
    ])

# Кнопки управления новостями
def get_news_keyboard(category, url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Читать тут", web_app=WebAppInfo(url=url))],
        [InlineKeyboardButton(text="Предыдущая", callback_data=f"prev_{category}"),
         InlineKeyboardButton(text="Следующая", callback_data=f"next_{category}")],
        [InlineKeyboardButton(text="Меню", callback_data="menu")]
    ])

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    logging.info("Пользователь вызвал /start")
    await message.answer("Привет! Выбери категорию:", reply_markup=get_main_menu())

# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    logging.info("Пользователь вызвал /help")
    await message.answer("Команды:\n"
                         "/start - Главное меню\n"
                         "/help - Показать это сообщение\n\n"
                         "Выбери категорию для просмотра новостей.")

# Показ главного меню (по кнопке "Меню")
@dp.callback_query(lambda c: c.data == "menu")
async def show_menu(callback: types.CallbackQuery):
    logging.info("Пользователь вернулся в меню")
    try:
        await callback.message.edit_text("Выбери категорию:", reply_markup=get_main_menu())
    except Exception as e:
        logging.error(f"Ошибка при возвращении в меню: {e}")
        await callback.message.answer("Выбери категорию:", reply_markup=get_main_menu())
    finally:
        await callback.answer()

# Функция отображения новости
async def show_news(callback: types.CallbackQuery, category: str, index: int):
    all_news = news_data.get(category, [])
    if not all_news:
        logging.warning(f"В категории {category} нет новостей.")
        await callback.message.edit_text("Новостей не найдено. Попробуйте позже.", reply_markup=get_main_menu())
        return

    # Зацикливание индекса
    if index < 0:
        index = len(all_news) - 1
    elif index >= len(all_news):
        index = 0
    current_index[category] = index

    # Данные текущей новости
    news = all_news[index]
    logging.debug(f"Показ новости {index}: {news}")

    title = news.get("title", "Нет заголовка")
    url = news.get("url", "#")
    image = news.get("image", default_image)
    date = news.get("date", "Не указана")

    caption = f"<b>{title}</b>\n\nДата: {date}\n\n<a href='{url}'>Читать полностью</a>"
    keyboard = get_news_keyboard(category, url)

    try:
        # Если сообщение содержит медиа (например, фото)
        if callback.message.photo:
            await callback.message.edit_media(
                media=InputMediaPhoto(media=image, caption=caption, parse_mode="HTML"),
                reply_markup=keyboard
            )
        else:
            # Если сообщение текстовое
            await callback.message.edit_text(caption, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка при показе новости: {e}")
        await callback.message.answer_photo(photo=image, caption=caption, parse_mode="HTML", reply_markup=keyboard)

    await callback.answer()

# Загрузка новостей
@dp.callback_query(lambda c: c.data in ["tech_news", "game_news"])
async def load_news(callback: types.CallbackQuery):
    category = callback.data
    logging.info(f"Загрузка новостей для категории: {category}")

    # Загрузка новостей
    if category == "tech_news":
        news_data[category] = get_tech_news()
    elif category == "game_news":
        news_data[category] = get_game_news()

    logging.debug(f"Новости для {category}: {news_data[category]}")

    if not news_data[category]:
        logging.warning(f"Новости для {category} не найдены.")
        await callback.message.edit_text("К сожалению, новости не найдены. Попробуйте позже.",
                                         reply_markup=get_main_menu())
        return

    current_index[category] = 0
    await show_news(callback, category, 0)

# Переключение новостей
@dp.callback_query(lambda c: c.data.startswith("prev_") or c.data.startswith("next_"))
async def paginate_news(callback: types.CallbackQuery):
    try:
        action, category = callback.data.split("_", 1)  # Учитываем, что данные могут содержать больше одного "_"
        current_idx = current_index.get(category, 0)

        if action == "prev":
            current_idx -= 1
        elif action == "next":
            current_idx += 1

        logging.info(f"Переключение новости: {action} (индекс {current_idx})")
        await show_news(callback, category, current_idx)
    except Exception as e:
        logging.error(f"Ошибка в переключении новостей: {e}")

# Главный обработчик
async def main():
    logging.info("Запуск бота")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
