from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from src.models import User
from src.utils.message_helpers import get_user_text


async def handle_get_profile(
    message: Message,
    bot: AsyncTeleBot,
    session: AsyncSession,
    user: User,
    state: StateContext,
):
    if not user.registered:
        await bot.send_message(
            message.chat.id, "Ты еще не зарегистрирован, нажми /register"
        )
    else:
        await bot.send_message(
            message.chat.id, get_user_text(user)
        )
