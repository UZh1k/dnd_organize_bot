import os
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT")
CONNECTION_TYPE = os.getenv("CONNECTION_TYPE")
WEBHOOK_URL_BASE = os.getenv("WEBHOOK_URL_BASE")
WEBHOOK_IP = os.getenv("WEBHOOK_IP")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT")

BOT_USERNAME = os.getenv("BOT_USERNAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL_PATH = f"/{BOT_TOKEN}/"
DB_URL = os.getenv("DB_URL")
STATE_STORAGE = os.getenv("STATE_STORAGE")
REDIS_URL = os.getenv("REDIS_URL")
REDIS_PORT = os.getenv("REDIS_PORT")

NEWS_CHANNEL_ID: int = int(os.getenv("NEWS_CHANNEL_ID"))
ADMIN_IDS: list[int] = list(map(int, os.getenv("ADMIN_IDS").split(",")))
EXCEPTION_CHAT_ID: int = int(os.getenv("EXCEPTION_CHAT_ID"))

ALLOWED_UPDATE_TYPES = [
    "my_chat_member",
    "new_chat_member",
    "chat_member",
    "message",
    "callback_query",
    "photo",
    "document",
]

START_IMAGE = os.getenv("START_IMAGE")
ABOUT_IMAGE = os.getenv("ABOUT_IMAGE")
REGISTER_IMAGE = os.getenv("REGISTER_IMAGE")
SEARCH_IMAGE = os.getenv("SEARCH_IMAGE")
CREATE_IMAGE = os.getenv("CREATE_IMAGE")
FEEDBACK_IMAGE = os.getenv("FEEDBACK_IMAGE")

BOOSTY_LINK = os.getenv("BOOSTY_LINK")
CRYPTO_LINK = os.getenv("CRYPTO_LINK")
