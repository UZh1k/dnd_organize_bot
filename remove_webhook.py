import asyncio

from main import bot

async def remove_webhook():
    await bot.remove_webhook()

asyncio.run(remove_webhook())
