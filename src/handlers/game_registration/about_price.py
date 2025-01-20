from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from src.handlers.game_registration.states import GameRegistrationStates
from src.models import User
from src.utils.form.form_text_item import FormTextItem


class GameRegistrationAboutPrice(FormTextItem):
    state = GameRegistrationStates.about_price
    prepare_text = (
        "Укажи стоимость своей игры. Если стоимость не фиксированная, "
        "то опиши от чего она зависит."
    )
    message_length = 40

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(about_price=text)