from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from consts import ADMIN_IDS
from handlers.administration.settings import SendNotificationStates
from models import User
from utils.handlers.base_message_handler import BaseMessageHandler


class NotificationCustomFilterHandler(BaseMessageHandler):

    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            state=SendNotificationStates.custom_filter,
            content_types=["text"],
            func=lambda message: message.chat.id in ADMIN_IDS,
            chat_types=["private"],
        )

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        await self.bot.send_message(
            message.chat.id,
            "Напиши сообщение, которое отправится всем, "
            "кого ты выбрал (без дупликатов)"
        )
        await state.set(SendNotificationStates.handle_text)
        await state.add_data(custom_filter=message.text)
