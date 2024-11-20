from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem


class FormChoiceItem(FormChoiceTextItem):
    with_message = False

    async def handle_message(
            self,
            message: Message,
            bot: AsyncTeleBot,
            user: User,
            session: AsyncSession,
            state: StateContext,
    ): ...
