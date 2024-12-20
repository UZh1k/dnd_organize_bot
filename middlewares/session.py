from datetime import datetime

from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.types import Message, Update

from consts import ALLOWED_UPDATE_TYPES
from db import async_session


class SessionMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ALLOWED_UPDATE_TYPES

    @classmethod
    async def _provide_session(cls, data: dict) -> dict:
        data["session"] = async_session()
        return data

    @classmethod
    async def _on_close(cls, data: dict, exception):
        if session := data.get("session"):
            if not exception:
                if db_user := data.get("user"):
                    db_user.commands_count += 1
                    db_user.last_update = datetime.now()
                await session.commit()
            await session.close()

    async def pre_process(self, update: Update | Message, data: dict):
        return await self._provide_session(data)

    async def post_process(self, update: Update | Message, data: dict, exception):
        await self._on_close(data, exception)
