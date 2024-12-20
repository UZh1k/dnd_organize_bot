from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_text_item import FormTextItem


class GameRegistrationStartLevel(FormTextItem):
    state = GameRegistrationStates.start_level
    prepare_text = "Какой уровень будет искателей приключений в твоей игре на старте?"
    message_length = 40

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(start_level=text)
