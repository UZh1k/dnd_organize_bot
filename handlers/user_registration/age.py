from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from handlers.user_registration.states import RegistrationStates
from models import User
from utils.form_text_item import FormTextItem


class UserRegistrationAge(FormTextItem):
    state = RegistrationStates.age
    prepare_text = "Введи свой возраст"

    @classmethod
    async def validate_answer(cls, message: Message, bot: AsyncTeleBot) -> bool:
        if not message.text.isdigit():
            await bot.send_message(message.chat.id, "Введи число")
            return False
        if not 10 < int(message.text) < 100:
            await bot.send_message(
                message.chat.id, "Мне жаль, но ты не подходишь по возрасту"
            )
            return False
        return True

    async def save_answer(self, text: str, user: User, session: AsyncSession):
        user.age = int(text)
