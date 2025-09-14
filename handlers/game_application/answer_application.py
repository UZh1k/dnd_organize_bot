from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from controllers.game import GameController
from controllers.game_application import GameApplicationController
from models import User
from utils.handlers.base_message_handler import BaseMessageHandler


class AnswerApplicationHandler(BaseMessageHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            content_types=[
                "text",
                "photo",
                "voice",
                "audio",
                "video_note",
            ],
            func=lambda message: message.reply_to_message,
            chat_types=["private"],
        )

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        application = await GameApplicationController.get_one_for_answer(
            user.id, message.reply_to_message.id, session
        )
        if not application:
            return

        game = await GameController.get_one(application.game_id, session)
        await self.bot.send_message(
            application.user_id,
            f'Ответ от мастера {user.name} по игре "{game.title}"',
        )
        await self.bot.copy_message(
            application.user_id,
            message.chat.id,
            message.id,
        )

        await self.bot.send_message(message.chat.id, "Сообщение отправлено")
