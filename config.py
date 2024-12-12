import os
from dotenv import load_dotenv

load_dotenv()  # загрузка переменных из .env файла

BOT_TOKEN = os.getenv('BOT_TOKEN')