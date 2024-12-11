import requests
from bs4 import BeautifulSoup

def get_game_news():
    url = "https://www.playground.ru/news"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")

    # Ищем блоки с новостями
    # Судя по скриншоту, новости находятся в div с классом "post".
    posts = soup.find_all("div", class_="post", limit=5)
    news_list = []

    for post in posts:
        # Заголовок
        title_tag = post.find("div", class_="post-title").find("a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        news_url = title_tag.get("href", "")
        if not news_url.startswith("http"):
            news_url = "https://www.playground.ru" + news_url

        # Попытка найти картинку: обычно она может быть в div с классом "post-content"
        # или "post-flow-image". Если картинки нет - будет None
        # Рассмотрим, что внутри post может быть figure или img
        img_tag = post.find("figure", class_="post-image")
        if img_tag:
            # Внутри figure может быть img
            img = img_tag.find("img")
            if img:
                image_url = img.get("src")
            else:
                image_url = None
        else:
            image_url = None

        # Рейтинг
        rating_tag = post.find("span", class_="post-rating-counter")
        if rating_tag:
            # Можно достать значение из атрибута title или из вложенного span.value
            value_tag = rating_tag.find("span", class_="value")
            if value_tag:
                rating = value_tag.get_text(strip=True)
            else:
                rating = rating_tag.get("title", "0")
        else:
            rating = "0"

        # Дата не извлекаем, если нужно - можно добавить логику

        news_list.append({
            "title": title,
            "url": news_url,
            "image": image_url,
            "likes": rating,  # переиспользуем поле 'likes' под рейтинг
            "date": None
        })

    return news_list
