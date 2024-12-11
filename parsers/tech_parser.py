import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser as date_parser

def get_ai_news_last_24h():
    url = "https://3dnews.ru/tags/%D0%B8%D0%B8"
    response = requests.get(url)
    if response.status_code != 200:
        print("Не удалось получить страницу.")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    articles = soup.select("#allnews div.article-entry")
    news_list = []

    # Текущее время
    now = datetime.now()
    twenty_four_hours_ago = now - timedelta(hours=24)

    for article in articles:
        # Заголовок
        header_tag = article.select_one("a.entry-header")
        if not header_tag:
            continue
        title = header_tag.get_text(strip=True)
        news_url = header_tag.get("href", "")
        if news_url and news_url.startswith("/"):
            news_url = "https://3dnews.ru" + news_url

        # Дата
        time_tag = article.select_one("time.article-time")
        if not time_tag:
            continue

        # Попытаемся сначала взять дату из атрибута datetime, если он есть
        if time_tag.has_attr("datetime"):
            dt_str = time_tag["datetime"]  # Например: 2024-12-11T13:37:00+03:00
            # Используем dateutil для парсинга ISO 8601 с зоной
            pub_date = date_parser.isoparse(dt_str)
        else:
            # Если нет datetime, распарсим текст. Например: "11.12.2024, 13:37"
            date_text = time_tag.get_text(strip=True)
            # Предполагаемый формат: DD.MM.YYYY, HH:MM
            # Проверить реальный формат на странице и подстроить
            pub_date = datetime.strptime(date_text, "%d.%m.%Y, %H:%M")

        # Картинка
        img_tag = article.select_one("a.entry-image-link img")
        image_url = None
        if img_tag:
            image_url = img_tag.get("src")
            if image_url and image_url.startswith("//"):
                image_url = "https:" + image_url

        # Фильтруем по дате: берем только новости, более "свежие" чем 24 часа назад
        if pub_date > twenty_four_hours_ago:
            news_list.append({
                "title": title,
                "url": news_url,
                "image": image_url,
                "date": pub_date.strftime("%d.%m.%Y %H:%M")
            })

    return news_list

if __name__ == "__main__":
    news = get_ai_news_last_24h()
    for n in news:
        print(f"Заголовок: {n['title']}")
        print(f"Дата: {n['date']}")
        print(f"Ссылка: {n['url']}")
        print(f"Картинка: {n['image']}\n")
