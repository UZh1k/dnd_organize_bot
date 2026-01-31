from sqlalchemy.ext.asyncio import AsyncSession
from telebot.apihelper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import Message

from consts import ADMIN_IDS
from controllers.game import GameController
from handlers.group_administration.group_funcs import on_close_game
from models import User
from utils.handlers.base_message_handler import BaseMessageHandler


class CloseGameHandler(BaseMessageHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            commands=["close_game"],
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
                message.chat.id, 'Отправь сообщение в формате "/close_game 123" '
            )
            return
        game = await GameController.get_one(int(message_split[1]), session)
        if not game:
            await self.bot.send_message(message.chat.id, "Такой игры не существует")
            return
        await on_close_game(self.bot, game, session)

        try:
            await self.bot.send_message(
                game.creator_id,
                "С сожалением сообщаю, что моим администраторам пришлось закрыть "
                f"твой набор на игру под названием {game.title}.\n\n"
                "Скорее всего, пост нарушал одно из наших правил:\n"
                "1. Бот используется строго для поиска игроков на конкретную игру. "
                "Большая часть наборов, созданных для иных целей - таких как сервер "
                "по Minecraft, онлайн-школа, вакансия ГМа, поиск редакторов и "
                "так далее - удаляется.\n"
                "2. Часть текста поста нарушает законы РФ.\n\n"
                "Пожалуйста, придерживайся наших правил, и мы будем рады видеть "
                "новые наборы от тебя!",
            )
        except ApiTelegramException:
            pass

        await self.bot.send_message(
            message.chat.id,
            "Игра закрыта, и пользователь получил предупреждение.",
        )
