from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from consts import FEEDBACK_CHAT_ID, BOT_USERNAME
from models import User
from utils.handlers.base_message_handler import BaseMessageHandler


class AnswerHandler(BaseMessageHandler):

    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            content_types=[
                "text",
                "photo",
                "document",
                "video",
                "voice",
                "audio",
                "video_note",
            ],
            func=lambda message: (
                message.chat.id == FEEDBACK_CHAT_ID
                and message.reply_to_message
                and message.reply_to_message.from_user.username == BOT_USERNAME
                and message.reply_to_message.forward_origin
            ),
        )

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        await self.bot.send_message(
            message.reply_to_message.forward_origin.sender_user.id,
            "Сники Бот Тим (для ответа на это сообщение отправь команду /feedback):",
        )
        await self.bot.copy_message(
            message.reply_to_message.forward_origin.sender_user.id,
            message.chat.id,
            message.id,
        )

        await self.bot.send_message(message.chat.id, "Сообщение отправлено")
