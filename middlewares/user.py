from telebot.types import Message, Update, User as TGUser
from telebot.asyncio_handler_backends import BaseMiddleware, SkipHandler

from consts import ALLOWED_UPDATE_TYPES
from controllers.user import UserController


class UserMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ALLOWED_UPDATE_TYPES

    @classmethod
    async def _provide_user(cls, user: TGUser, data: dict):
        if not user:
            data["user"] = None
        elif session := data.get("session"):
            db_user = await UserController.get_or_create(
                user.id,
                "id",
                session,
                {"username": getattr(user, "username")},
            )
            if db_user.banned:
                return SkipHandler()
            db_user.commands_count += 1
            data["user"] = db_user
        return data

    async def pre_process(self, update: Update | Message, data: dict) -> dict:
        return await self._provide_user(update.from_user, data)

    async def post_process(self, update: Update | Message, data: dict, exception):
        pass
