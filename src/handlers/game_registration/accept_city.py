from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from src.handlers.game_registration.city import GameRegistrationCity
from src.handlers.game_registration.states import GameRegistrationStates
from src.models import User
from src.utils.form.form_choice_item import FormChoiceItem


class GameRegistrationAcceptCity(FormChoiceItem):
    state = GameRegistrationStates.accept_city
    prepare_text = "Ты хочешь провести игру в своем городе - {user.city.name}?"
    form_item_name = "accept_city"

    alert_message = None
    choices = (
        ("Да", "yes"),
        ("Нет", "no"),
    )

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        if text == "yes":
            await state.add_data(city_id=user.city_id)

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        if answer == "no":
            await GameRegistrationCity.prepare(
                chat_id, user, session, bot, state, self.form_prefix
            )
        else:
            await self.next_step(chat_id, user, session, bot, state, self.form_prefix)
