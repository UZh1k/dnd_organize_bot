from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Update

from controllers.game import GameController
from models import User


async def handle_bot_added_to_group(
    update: Update, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    await bot.send_message(update.chat.id, "Теперь сделай бота админом")


async def handle_bot_removed_group(
    update: Update, bot: AsyncTeleBot, session: AsyncSession, user: User
):
    await GameController.unlink_game_from_group(update.chat.id, session)
    # todo delete message from channel
