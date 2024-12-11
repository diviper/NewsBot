import requests
from bs4 import BeautifulSoup

def get_tech_news():
    url = "https://gagadget.com/news/ai/"
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/110.0.0.0 Safari/537.36")
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")

    # Попробуем найти все ссылки a.cell-liner (каждая может быть новостью)
    items = soup.select("a.cell-liner")
    news_list = []

    for item in items[:10]:
        img_tag = item.find("img", class_="b-respon-img")
        if not img_tag:
            continue
        title = img_tag.get("alt", "Без заголовка").strip()
        news_url = item.get("href", "")
        if news_url and not news_url.startswith("http"):
            news_url = "https://gagadget.com" + news_url

        # Попытка найти дату в следующем блоке cell-desc
        # Предполагаем, что div.cell-desc идёт после a.cell-liner
        parent = item.parent
        date = None
        if parent:
            desc = parent.find("div", class_="cell-desc")
            if desc:
                date = desc.get_text(strip=True)

        # Картинка
        image_url = img_tag.get("src")
        if image_url and image_url.startswith("/"):
            image_url = "https://gagadget.com" + image_url

        news_list.append({
            "title": title,
            "url": news_url,
            "image": image_url,
            "likes": None,
            "date": date
        })

    return news_list
