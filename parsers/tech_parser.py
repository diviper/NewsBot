import requests
from bs4 import BeautifulSoup

def get_tech_news():
    url = "https://3dnews.ru/tags/ии"
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/110.0.0.0 Safari/537.36")
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    articles = soup.find_all("div", class_="article-entry", limit=10)
    news_list = []

    for article in articles:
        try:
            # Заголовок и ссылка
            title_tag = article.find("a", class_="entry-header")
            if not title_tag:
                continue
            title = title_tag.find("h1").get_text(strip=True)
            news_url = title_tag.get("href", "")
            if news_url and not news_url.startswith("http"):
                news_url = "https://3dnews.ru" + news_url

            # Дата публикации (если доступна)
            date_tag = article.find("div", class_="entry-info")
            date = date_tag.get_text(strip=True) if date_tag else None

            # Картинка (если есть)
            image_url = None
            img_tag = article.find("img")
            if img_tag:
                image_url = img_tag.get("src")
                if image_url and image_url.startswith("//"):
                    image_url = "https:" + image_url

            news_list.append({
                "title": title,
                "url": news_url,
                "image": image_url,
                "likes": None,  # Лайки не отображаются
                "date": date
            })
        except Exception as e:
            print(f"Ошибка обработки новости: {e}")
            continue

    return news_list
