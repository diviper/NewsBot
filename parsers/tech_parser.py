import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser as date_parser

def get_tech_news():
    url = "https://3dnews.ru/tags/%D0%B8%D0%B8"  # Новости по тегу ИИ
    response = requests.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")
    articles = soup.select("#allnews div.article-entry")
    news_list = []

    now = datetime.now()
    twenty_four_hours_ago = now - timedelta(hours=24)

    for article in articles:
        # Заголовок и ссылка
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

        if time_tag.has_attr("datetime"):
            pub_date = date_parser.isoparse(time_tag["datetime"])
        else:
            date_text = time_tag.get_text(strip=True)
            pub_date = datetime.strptime(date_text, "%d.%m.%Y, %H:%M")

        # Картинка
        img_tag = article.select_one("a.entry-image-link img")
        image_url = None
        if img_tag:
            image_url = img_tag.get("src")
            if image_url and image_url.startswith("//"):
                image_url = "https:" + image_url

        if pub_date > twenty_four_hours_ago:
            news_list.append({
                "title": title,
                "url": news_url,
                "image": image_url,
                "date": pub_date.strftime("%d.%m.%Y %H:%M")
            })

    return news_list
