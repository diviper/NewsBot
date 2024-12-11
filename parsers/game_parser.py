import requests
from bs4 import BeautifulSoup
import re

def get_game_news():
    url = "https://www.playground.ru/news"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")
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

        figure = post.find("figure", class_="post-image")
        image_url = None
        if figure:
            style = figure.get("style", "")
            # Попытка найти background-image
            match = re.search(r'background-image:\s*url\("([^"]+)"\)', style)
            if match:
                image_url = match.group(1)

        meta_tag = post.find("div", class_="post-metadata")
        date = meta_tag.get_text(strip=True) if meta_tag else None

        rating_tag = post.find("span", class_="post-rating-counter")
        if rating_tag:
            value_tag = rating_tag.find("span", class_="value")
            rating = value_tag.get_text(strip=True) if value_tag else rating_tag.get("title", None)
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
