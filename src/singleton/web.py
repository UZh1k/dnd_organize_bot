from fastapi import FastAPI
from telebot.types import Update

import src.consts
from src.singleton.telegram import bot

app = FastAPI()


@app.post(src.consts.WEBHOOK_URL_PATH)
async def process_webhook(update: dict):
    """
    Process webhook calls
    """
    if update:
        update = Update.de_json(update)
        await bot.process_new_updates([update])
    else:
        return


@app.get("/", status_code=201)
async def health():
    return {}
