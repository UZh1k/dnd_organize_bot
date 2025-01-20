from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from src.models import User
from src.utils.form.form_text_item import FormTextItem


class FormPhotoItem(FormTextItem):
    with_photo = True
    with_message = False

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        return False

    async def handle_photo(
        self,
        message: Message,
        bot: AsyncTeleBot,
        user: User,
        session: AsyncSession,
        state: StateContext,
    ):
        if await self.validate_answer(message, bot):
            await self.save_answer(message.photo[-1].file_id, user, session, state)
            await self.on_answered(
                message.text, message.chat.id, user, session, bot, state
            )
