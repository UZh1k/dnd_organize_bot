from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from handlers.user_registration.states import UserRegistrationStates
from models import User
from utils.form.form_text_item import FormTextItem


class UserRegistrationName(FormTextItem):
    state = UserRegistrationStates.name
    prepare_text = "Введи имя"

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        if message.text.isdigit() or len(message.text) > 100:
            await bot.send_message(
                message.chat.id,
                "Для имени допускается настоящее имя "
                "или ник длиной не более 100 символов ",
            )
            return False
        return True

    async def save_answer(self, text: str, user: User, session: AsyncSession):
        user.name = text
