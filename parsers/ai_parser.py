# parsers/ai_parser.py
import requests
from bs4 import BeautifulSoup

def get_ai_news():
    # Здесь код для парсинга AI новостей с выбранного вами сайта.
    # Пока просто вернем примерный формат пустым списком.
    # Позже сюда можно добавить логику:
    # - requests.get(...)
    # - soup = BeautifulSoup(...)
    # - извлечь последние 5 новостей
    # Должен вернуться список словарей со структурой:
    # [{"title": "...", "url": "...", "image": "...", "likes": ..., "date": ...}, ...]
    return []
