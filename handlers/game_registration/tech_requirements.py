from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form import FormTextItem


class GameRegistrationTechRequirements(FormTextItem):
    state = GameRegistrationStates.tech_requirements
    prepare_text = (
        "Какие у тебя требования к игрокам? Есть ли требования к технике? "
        "Напиши подробнее в свободной форме."
    )

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(tech_requirements=text)
