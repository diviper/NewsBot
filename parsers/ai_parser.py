import requests
from bs4 import BeautifulSoup

def get_ai_news():
    url = "https://venturebeat.com/category/ai/"
    response = requests.get(url)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")

    # На странице VentureBeat/AI статьи перечислены в теге article с классом "ArticleListing__ArticleListItem-sc-...".
    # Пройдемся по ним, достанем первые 5.
    articles = soup.find_all("article", limit=5)
    news_list = []

    for article in articles:
        title_tag = article.find("h2")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)

        # Ссылка может быть в теге <a>
        link_tag = article.find("a")
        if not link_tag:
            continue
        news_url = link_tag.get("href")

        # Попытаемся найти картинку:
        # Обычно картинки внутри article <img> или в figure
        img_tag = article.find("img")
        if img_tag:
            image_url = img_tag.get("src")
        else:
            image_url = None

        # Дата не всегда легко достать, попробуем найти теги с датой
        # Если на сайте сложный формат - можно пропустить или поставить None.
        # Для начала поставим None или текущее время, чтобы не оставить пустым
        date = None

        # Лайки отсутствуют, поставим 0
        likes = 0

        news_list.append({
            "title": title,
            "url": news_url,
            "image": image_url,
            "likes": likes,
            "date": date
        })

    return news_list
