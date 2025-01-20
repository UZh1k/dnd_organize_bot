from sqlalchemy.ext.asyncio import AsyncSession
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import Message

from src.consts import ADMIN_IDS, NEWS_CHANNEL_ID
from src.controllers.game import GameController
from src.controllers.user import UserController
from src.models import User
from src.utils.handlers.base_message_handler import BaseMessageHandler


class BanGameHandler(BaseMessageHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            commands=["ban_game"],
            func=lambda message: message.chat.id in ADMIN_IDS,
        )

    async def handle_message(
        self,
        message: Message,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        message_split = message.text.split()
        if len(message_split) == 1 or not message_split[1].isdigit():
            await self.bot.send_message(
                message.chat.id, 'Отправь сообщение в формате "/ban_game 123" '
            )
            return
        game = await GameController.get_one(int(message_split[1]), session)
        if not game:
            await self.bot.send_message(message.chat.id, "Такой игры не существует")
            return
        game.active = False
        game.done = False
        user = await UserController.get_one(game.creator_id, session)
        user.banned = True
        await self.bot.send_message(
            message.chat.id, "Игра закрыта и пользователь забанен"
        )
        try:
            await self.bot.delete_message(NEWS_CHANNEL_ID, game.post_id)
        except ApiTelegramException:
            pass
