import requests
from bs4 import BeautifulSoup

def get_tech_news():
    url = "https://nplus1.ru/rubric/technology"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")

    # Статьи в div.rubric-page__material
    items = soup.find_all("div", class_="rubric-page__material", limit=10)
    news_list = []
    for item in items:
        a_tag = item.find("a", class_="rubric-page__link")
        if not a_tag:
            continue
        title = a_tag.get_text(strip=True)
        news_url = a_tag.get("href", "")
        if news_url and not news_url.startswith("http"):
            news_url = "https://nplus1.ru" + news_url

        # Дата
        date_tag = item.find("div", class_="rubric-page__info-date")
        date = date_tag.get_text(strip=True) if date_tag else None

        # Картинка
        img_tag = item.find("img", class_="rubric-page__image")
        if img_tag:
            image_url = img_tag.get("src")
            if image_url.startswith("//"):
                image_url = "https:" + image_url
        else:
            image_url = None

        news_list.append({
            "title": title,
            "url": news_url,
            "image": image_url,
            "likes": None,
            "date": date
        })

    return news_list
