import requests
from bs4 import BeautifulSoup

def get_tech_news():
    url = "https://rb.ru/tag/technology/"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")

    # Структура сайта rb.ru (на момент написания):
    # Список статей в div с классом "lenta__item"
    # Заголовок в a.lenta__title
    # Дата в span.lenta__date
    # Картинка в img.lenta__image
    articles = soup.find_all("div", class_="lenta__item", limit=10)
    news_list = []

    for article in articles:
        title_tag = article.find("a", class_="lenta__title")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        news_url = title_tag.get("href")
        if news_url and not news_url.startswith("http"):
            news_url = "https://rb.ru" + news_url

        # Дата
        date_tag = article.find("span", class_="lenta__date")
        date = date_tag.get_text(strip=True) if date_tag else None

        # Картинка
        img_tag = article.find("img", class_="lenta__image")
        if img_tag:
            image_url = img_tag.get("src")
            if image_url and image_url.startswith("//"):
                image_url = "https:" + image_url
        else:
            image_url = None

        # Рейтинг/лайки в данном случае не предусмотрены, поставим None
        news_list.append({
            "title": title,
            "url": news_url,
            "image": image_url,
            "likes": None,
            "date": date
        })

    return news_list
