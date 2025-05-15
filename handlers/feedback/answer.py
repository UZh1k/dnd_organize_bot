from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from consts import FEEDBACK_CHAT_ID, BOT_USERNAME
from controllers.feedback_message import FeedbackMessageController
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
        reply_to_id = None
        if feedback_message := await FeedbackMessageController.get_one(
            message.reply_to_message.message_id, session, "message_id"
        ):
            reply_to_id = feedback_message.creator_id
        elif message.reply_to_message.forward_origin.type == "user":
            reply_to_id = message.reply_to_message.forward_origin.sender_user.id

        if not reply_to_id:
            await self.bot.send_message(
                message.chat.id, "Не нашли, кому отправлять сообщение :("
            )
            return

        await self.bot.send_message(
            reply_to_id,
            "Сники Бот Тим (для ответа на это сообщение отправь команду /feedback):",
        )
        await self.bot.copy_message(
            reply_to_id,
            message.chat.id,
            message.id,
        )

        await self.bot.send_message(message.chat.id, "Сообщение отправлено")
