from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.user_registration.states import UserRegistrationStates
from models import User
from utils.form.form_text_item import FormTextItem


class UserRegistrationBio(FormTextItem):
    state = UserRegistrationStates.bio
    prepare_text = (
        "И последний вопрос. Расскажи немного о себе. Как давно ты играешь или "
        "ведешь игры? Какие системы тебе нравятся? Какими вселенными увлекаешься? "
        "Напиши мне ответ в свободной форме. Ответ станет твоим описанием."
    )

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        if len(message.text) > 800:
            await bot.send_message(
                message.chat.id,
                "Мне кажется, что твое описание слишком большое и не "
                "вместится в пост. Пожалуйста, напиши немного короче.",
            )
            return False
        return True

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        user.bio = text
