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

    # Ищем новости в div.post (каждая новость - отдельный пост)
    posts = soup.find_all("div", class_="post", limit=10)
    news_list = []

    for post in posts:
        # Заголовок
        title_div = post.find("div", class_="post-title")
        if not title_div:
            continue
        a_tag = title_div.find("a")
        if not a_tag:
            continue
        title = a_tag.get_text(strip=True)
        news_url = a_tag.get("href", "")
        if news_url and not news_url.startswith("http"):
            news_url = "https://www.playground.ru" + news_url

        # Дата
        meta_tag = post.find("div", class_="post-metadata")
        date = meta_tag.get_text(strip=True) if meta_tag else None

        # Картинка
        # Ищем figure, внутри picture -> img
        figure_tag = post.find("figure")
        image_url = None
        if figure_tag:
            picture_tag = figure_tag.find("picture")
            if picture_tag:
                img_tag = picture_tag.find("img")
                if img_tag:
                    image_url = img_tag.get("src")
                    if image_url and image_url.startswith("//"):
                        image_url = "https:" + image_url

        news_list.append({
            "title": title,
            "url": news_url,
            "image": image_url,
            "likes": None,
            "date": date
        })

    return news_list
