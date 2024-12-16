from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.user_registration.city import UserRegistrationCity
from handlers.user_registration.states import UserRegistrationStates
from models import User
from utils.form.form_text_item import FormTextItem


class UserRegistrationAge(FormTextItem):
    state = UserRegistrationStates.age
    prepare_text = (
        "Сколько тебе лет? Введи значение от 14 до 99 лет. Если ты младше 14, "
        "то к сожалению, тебе нельзя использовать бота. Но обязательно возвращайся, "
        "когда подрастешь."
    )

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        if not message.text.isdigit():
            await bot.send_message(message.chat.id, "Введи число")
            return False
        if not 13 < int(message.text) < 100:
            await bot.send_message(
                message.chat.id,
                "Не смог разобрать твой ответ, пожалуйста, попробуй написать по-другому",
            )
            return False
        return True

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        if int(answer) < 18:
            await self.next_step(chat_id, user, session, bot, state)
        else:
            await UserRegistrationCity.prepare(chat_id, user, session, bot, state)

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        user.age = int(text)
