import os
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT")
BOT_USERNAME = os.getenv("BOT_USERNAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_URL = os.getenv("DB_URL")
POST_CHANNEL_ID: int = int(os.getenv("POST_CHANNEL_ID"))
ADMIN_IDS: list[int] = list(map(int, os.getenv("ADMIN_IDS").split(",")))
