from telebot.types import Message, Update, User as TGUser
from telebot.asyncio_handler_backends import BaseMiddleware

from controllers.user import UserController


class UserMiddleware(BaseMiddleware):
    def __init__(self):
        # self.update_sensitive = True
        self.update_types = ["message", "callback_query"]

    @classmethod
    async def _provide_user(cls, user: TGUser, data: dict):
        if session := data.get("session"):
            data["user"] = await UserController.get_or_create(
                user.id,
                "id",
                session,
                {"username": getattr(user, "username")},
            )
        return data

    async def pre_process(self, update: Update | Message, data: dict) -> dict:
        return await self._provide_user(update.from_user, data)

    async def post_process(
        self, update: Update | Message, data: dict, exception
    ):
        pass
