from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from src.consts import ADMIN_IDS
from src.controllers.user import UserController
from src.models import User
from src.utils.handlers.base_message_handler import BaseMessageHandler


class BanHandler(BaseMessageHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            commands=["ban"],
            func=lambda message: message.chat.id in ADMIN_IDS,
        )

    async def on_action(self, message: Message, user: User):
        user.banned = True
        await self.bot.send_message(message.chat.id, "Пользователь забанен")

    async def handle_message(
        self,
        message: Message,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        message_split = message.text.split()
        if len(message_split) == 1:
            await self.bot.send_message(
                message.chat.id, 'Отправь сообщение в формате "/ban 123" '
            )
            return

        user = await UserController.get_by_id_or_username(message_split[1], session)
        if not user:
            await self.bot.send_message(
                message.chat.id, "Такого пользователя не существует"
            )
            return

        await self.on_action(message, user)
