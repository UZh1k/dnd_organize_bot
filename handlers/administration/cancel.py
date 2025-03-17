from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from models import User
from utils.handlers.base_message_handler import BaseMessageHandler


class CancelHandler(BaseMessageHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            commands=["cancel"],
            chat_types=["private"],
        )

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        await state.delete()
        await self.bot.send_message(message.chat.id, "Отмена текущего действия")
