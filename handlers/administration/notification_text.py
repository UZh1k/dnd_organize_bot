import asyncio
from itertools import batched

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import Message

from consts import ADMIN_IDS
from controllers.user import UserController
from handlers.administration.settings import SendNotificationStates
from models import User
from utils.handlers.base_message_handler import BaseMessageHandler


class NotificationTextHandler(BaseMessageHandler):
    batch_size: int = 1  # never more than 30! Read docs

    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            state=SendNotificationStates.handle_text,
            func=lambda message: message.chat.id in ADMIN_IDS,
            chat_types=["private"],
        )

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        text = message.text
        users = await UserController.get_list(session, User.banned.is_(False))
        total_count = len(users)
        await self.bot.send_message(
            message.chat.id, f"Начинаем отправлять нотификации. Всего - {total_count}"
        )
        counter = 0
        for users_batch in batched(users, self.batch_size):
            for user in users_batch:
                try:
                    await self.bot.send_message(user.id, text)
                except ApiTelegramException as e:
                    print(e)
                    pass
            counter += len(users_batch)
            await self.bot.send_message(
                message.chat.id,
                f"{counter}/{total_count}"
            )
            await asyncio.sleep(1)
        await self.bot.send_message(message.chat.id, "Все нотификации отправлены")
