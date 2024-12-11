import requests
from bs4 import BeautifulSoup

def get_game_news():
    url = "https://www.playground.ru/news"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")

    # На странице новости представлены в виде карточек с классом "article__content"
    # или похожим, нужно посмотреть структуру. Попробуем найти элементы статей:
    articles = soup.find_all("div", class_="article-card__info", limit=5)
    news_list = []

    for article in articles:
        # Заголовок
        title_tag = article.find("a", class_="article-card__title-link")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)

        news_url = title_tag.get("href")
        # Убедимся, что ссылка абсолютная:
        if not news_url.startswith("http"):
            news_url = "https://www.playground.ru" + news_url

        # Картинка
        # Обычно картинки могут быть в родительском блоке с классом "article-card__image"
        # но сейчас мы ищем в info. Посмотрим родителя:
        parent = article.parent
        img_tag = parent.find("img") if parent else None
        image_url = img_tag.get("src") if img_tag else None

        # Лайки поставим 0, дату пока None:
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
