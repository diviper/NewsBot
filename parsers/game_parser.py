import requests
from bs4 import BeautifulSoup

def get_game_news():
    url = "https://www.playground.ru/news"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")

    # Найдём контейнеры с новостями
    # По состоянию на момент написания, новости на playground.ru представлены карточками с классом article-card
    articles = soup.find_all("div", class_="article-card", limit=5)
    news_list = []

    for article in articles:
        title_tag = article.find("a", class_="article-card__title-link")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        news_url = title_tag.get("href")

        if not news_url.startswith("http"):
            news_url = "https://www.playground.ru" + news_url

        # Картинка:
        img_tag = article.find("img", class_="article-card__image-img")
        image_url = img_tag.get("src") if img_tag else None

        # Лайки нет, ставим 0, дата None:
        likes = 0
        date = None

        news_list.append({
            "title": title,
            "url": news_url,
            "image": image_url,
            "likes": likes,
            "date": date
        })

    return news_list
