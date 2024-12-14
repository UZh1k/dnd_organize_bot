from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form import FormTextItem


class GameRegistrationTechRequirements(FormTextItem):
    state = GameRegistrationStates.tech_requirements
    prepare_text = (
        "Какие у тебя требования к игрокам? Есть ли требования к технике? "
        "Напиши подробнее в свободной форме."
    )

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        return await self.check_message_length(message, bot, message_length=100)

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(tech_requirements=text)
