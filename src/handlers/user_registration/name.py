from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from src.handlers.user_registration.states import UserRegistrationStates
from src.models import User
from src.utils.form.form_text_item import FormTextItem


class UserRegistrationName(FormTextItem):
    state = UserRegistrationStates.name
    prepare_text = (
        "Начинаем! Как игроки и мастера могут к тебе обращаться? "
        "Достаточно будет имени или никнейма. Отправь ответным сообщением."
    )
    message_length = 100

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        if await self.check_is_not_digit(message, bot):
            return await super().validate_answer(message, bot)
        return False

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        user.name = text
