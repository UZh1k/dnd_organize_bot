from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from src.handlers.game_registration.states import GameRegistrationStates
from src.models import User
from src.utils.form.form_text_item import FormTextItem


class GameRegistrationTitle(FormTextItem):
    state = GameRegistrationStates.title
    prepare_text = (
        "Придумай короткое название для твоей игры. "
        "Напиши мне ответ в свободной форме."
    )
    message_length = 80

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(title=text)
