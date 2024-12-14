from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.user_registration.states import UserRegistrationStates
from models import User
from utils.form.form_text_item import FormTextItem


class UserRegistrationName(FormTextItem):
    state = UserRegistrationStates.name
    prepare_text = (
        "Начинаем! Как игроки и мастера могут к тебе обращаться? "
        "Достаточно будет имени или никнейма. Отправь ответным сообщением."
    )

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        if message.text.isdigit():
            await bot.send_message(
                message.chat.id,
                "Не смог разобрать твой ответ, пожалуйста, "
                "попробуй написать по-другому",
            )
            return False
        return await self.check_message_length(message, bot, message_length=100)

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        user.name = text
