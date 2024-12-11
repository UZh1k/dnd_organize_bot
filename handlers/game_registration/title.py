from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form import FormTextItem


class GameRegistrationTitle(FormTextItem):
    state = GameRegistrationStates.title
    prepare_text = (
        "Придумай короткое название для твоей игры. "
        "Напиши мне ответ в свободной форме."
    )

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        if len(message.text) > 100:
            await bot.send_message(
                message.chat.id,
                "Мне кажется, что твое название слишком большое и не "
                "вместится в пост. Пожалуйста, напиши немного короче.",
            )
            return False
        return True

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(title=text)
