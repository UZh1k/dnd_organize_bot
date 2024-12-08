from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form import FormTextItem


class GameRegistrationTitle(FormTextItem):
    state = GameRegistrationStates.title
    prepare_text = (
        "Придумай короткое название для твоей игры. "
        "Напиши мне ответ в свободной форме."
    )

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(title=text)