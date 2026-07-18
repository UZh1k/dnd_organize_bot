from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_text_item import FormTextItem


class GameRegistrationAboutPrice(FormTextItem):
    state = GameRegistrationStates.about_price
    message_length = 40
    prepare_text = (
        "Укажи стоимость своей игры. Если стоимость не фиксированная, "
        "то опиши от чего она зависит.\n\n"
        f"Пожалуйста, постарайся уместиться в {message_length} символов. "
        f"Это обусловлено ограничениями самого мессенджера, "
        f"посты не могут превышать определенной длины."
    )

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(about_price=text)
