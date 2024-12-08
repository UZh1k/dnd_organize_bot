from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.types import Update, Message

from consts import ALLOWED_UPDATE_TYPES, EXCEPTION_CHAT_ID


class ExceptionMiddleware(BaseMiddleware):
    def __init__(self, bot: AsyncTeleBot):
        self.update_types = ALLOWED_UPDATE_TYPES
        self.bot = bot
        super().__init__()

    async def pre_process(self, update: Update | Message, data: dict):
        pass

    async def post_process(self, update: Update | Message, data: dict, exception):
        if exception:
            await self.bot.send_message(EXCEPTION_CHAT_ID, str(exception))