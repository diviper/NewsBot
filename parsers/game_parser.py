import requests
from bs4 import BeautifulSoup

def get_game_news():
    url = "https://www.playground.ru/news"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")

    # Ищем блоки постов. Согласно предыдущей логике - div с классом "post"
    # Выберем 10 новостей (чтобы было, что листать)
    posts = soup.find_all("div", class_="post", limit=10)
    news_list = []

    for post in posts:
        title_tag = post.find("div", class_="post-title")
        if not title_tag:
            continue
        a_tag = title_tag.find("a")
        if not a_tag:
            continue
        title = a_tag.get_text(strip=True)
        news_url = a_tag.get("href", "")
        if news_url and not news_url.startswith("http"):
            news_url = "https://www.playground.ru" + news_url

        # Картинка
        # Попытка: images могут быть в figure.post-image > img
        figure = post.find("figure", class_="post-image")
        if figure:
            img_tag = figure.find("img")
            if img_tag:
                image_url = img_tag.get("src")
            else:
                image_url = None
        else:
            image_url = None

        # Дата
        # Судя по скриншоту, дата находится в div.post-metadata, там может быть текст типа "вчера в 20:13 | Обновления"
        meta_tag = post.find("div", class_="post-metadata")
        if meta_tag:
            date = meta_tag.get_text(strip=True)
        else:
            date = None

        # Рейтинг
        rating_tag = post.find("span", class_="post-rating-counter")
        if rating_tag:
            value_tag = rating_tag.find("span", class_="value")
            if value_tag:
                rating = value_tag.get_text(strip=True)
            else:
                rating = rating_tag.get("title", None)
        else:
            rating = None

        news_list.append({
            "title": title,
            "url": news_url,
            "image": image_url,
            "likes": rating,
            "date": date
        })

    return news_list
