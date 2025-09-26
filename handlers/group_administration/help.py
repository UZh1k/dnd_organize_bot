from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from models import User
from utils.handlers.base_message_handler import BaseMessageHandler


class GroupHelpHandler(BaseMessageHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            commands=["help", "list"],
            chat_types=["group", "supergroup"],
        )

    async def handle_message(
        self,
        message: Message,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        await self.bot.send_message(
            message.chat.id,
            "*Список команд в группе игры:*\n\n"
            "/update - для поднятия поста в канале, если не набрались игроки, "
            "или кто-то в последний момент отказался. "
            "Можно использовать в том числе после сбора игры.\n"
            "/done - когда собрал полную группу игроков, чтобы остановить поиск игроков. "
            "Дает возможность оставлять друг другу отзыва через команду /review в боте.\n"
            "/close - для закрытия игры, если передумал ее проводить.\n"
            "/help - для вывода команд бота в группе игры.\n\n"
            "Недавно мы добавили новую возможность - теперь можно возобновлять поиск "
            "уже собранной игры командой /update, обязательно попробуй!",
            parse_mode="Markdown",
        )
