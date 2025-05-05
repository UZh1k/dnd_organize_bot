import asyncio

from consts import WEBHOOK_URL_BASE, WEBHOOK_URL_PATH
from main import bot


async def set_webhook():
    await bot.remove_webhook()

    await bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

asyncio.run(set_webhook())
