# ParseNews Telegram Bot

## Описание
ParseNews - это Telegram-бот для парсинга и отображения новостей из различных источников.

## Возможности
- Получение новостей об искусственном интеллекте
- Получение игровых новостей

## Установка
1. Клонируйте репозиторий
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка
1. Создайте файл `.env` и добавьте токен Telegram-бота:
```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
```

## Запуск
```bash
python main.py
```

## Команды
- `/start` - Начало работы с ботом
- `/ai_news` - Получить новости об ИИ
- `/game_news` - Получить игровые новости

## Технологии
- Python
- Aiogram
- BeautifulSoup
- aiohttp
