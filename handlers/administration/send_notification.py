from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from consts import ADMIN_IDS
from handlers.administration.settings import SendNotificationStates
from models import User
from utils.handlers.base_message_handler import BaseMessageHandler
from utils.other import is_command


class SendNotificationHandler(BaseMessageHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            commands=["send_notification"],
            func=(
                lambda message: message.chat.id in ADMIN_IDS
            ),
            chat_types=["private"],
        )

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        await self.bot.send_message(
            message.chat.id,
            "Напиши сообщение без медиа, которое я разошлю всем участникам. "
            "Внимательно проверь грамматику и все остальное, потому что изменить "
            "сообщение будет нельзя!",
        )
        await state.set(SendNotificationStates.handle_text)
