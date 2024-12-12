# formatters.py
def format_news_list(news_list):
    text = ""
    for news in news_list:
        # Допустим, у нас есть title, url, image, likes
        text += f"<b>{news['title']}</b>\n"
        text += f"Ссылка: {news['url']}\n"
        text += f"Лайков: {news['likes']}\n\n"
    return text
