import requests
from bs4 import BeautifulSoup

def get_tech_news():
    url = "https://rb.ru/tag/technology/"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")

    # Статьи в li.lenta__item
    items = soup.find_all("li", class_="lenta__item", limit=10)
    news_list = []
    for item in items:
        title_tag = item.find("a", class_="lenta__title")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        news_url = title_tag.get("href", "")
        if news_url and not news_url.startswith("http"):
            news_url = "https://rb.ru" + news_url

        date_tag = item.find("span", class_="lenta__date")
        date = date_tag.get_text(strip=True) if date_tag else None

        img_tag = item.find("img", class_="lenta__image")
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
            "likes": None,  # Здесь нет рейтинга, оставим None
            "date": date
        })

    return news_list
