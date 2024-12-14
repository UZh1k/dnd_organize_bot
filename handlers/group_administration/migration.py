from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from controllers.game import GameController
from models import User


async def handle_group_migrated(
    message: Message, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    game = await GameController.get_one(message.chat.id, session, "group_id")
    if not game:
        return
    game.group_id = message.migrate_to_chat_id
