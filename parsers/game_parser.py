import requests
from bs4 import BeautifulSoup

def get_game_news():
    url = "https://www.playground.ru/news"
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/110.0.0.0 Safari/537.36")
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")
    articles = soup.find_all("article", class_="article-card", limit=10)
    news_list = []
    for article in articles:
        title_tag = article.find("a", class_="article-card__title-link")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        news_url = title_tag.get("href", "")
        if news_url and not news_url.startswith("http"):
            news_url = "https://www.playground.ru" + news_url

        img_tag = article.find("img", class_="article-card__image-img")
        image_url = None
        if img_tag:
            image_url = img_tag.get("data-src") or img_tag.get("src")
            if image_url and image_url.startswith("//"):
                image_url = "https:" + image_url

        time_tag = article.find("span", class_="article-card__time")
        date = time_tag.get_text(strip=True) if time_tag else None

        news_list.append({
            "title": title,
            "url": news_url,
            "image": image_url,
            "likes": None,
            "date": date
        })

    return news_list
