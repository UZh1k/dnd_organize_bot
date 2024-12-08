from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.game_registration.game_time import GameRegistrationTime
from handlers.game_registration.states import GameRegistrationStates
from models import User
from utils.form.form_choice_item import FormChoiceItem


class GameRegistrationFree(FormChoiceItem):
    state = GameRegistrationStates.free
    prepare_text = "Ты планируешь провести игру за деньги или бесплатно?"
    form_name = "GameRegistration"
    form_item_name = "free"

    alert_message = "Ответ записан"
    choices = (
        ("Платно", "for_pay"),
        ("Бесплатно", "free"),
    )

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        await state.add_data(free=True if text == "free" else False)

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        if answer == "for_pay":
            await self.next_step(chat_id, user, session, bot, state)
        else:
            await GameRegistrationTime.prepare(chat_id, user, session, bot, state)
