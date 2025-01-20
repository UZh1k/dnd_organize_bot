from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from src.handlers.game_registration.states import GameRegistrationStates
from src.models import User
from src.utils.form.form_text_item import FormTextItem


class GameRegistrationTechRequirements(FormTextItem):
    state = GameRegistrationStates.tech_requirements
    prepare_text = (
        "Какие у тебя требования к игрокам? Есть ли требования к технике, например, "
        "наличие микрофона и камеры? Есть ли особые правила, например, запрет на "
        "алкоголь во время игры или запрет на использование телефона? Напиши подробнее "
        "в свободной форме."
    )
    message_length = 70

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(tech_requirements=text)
