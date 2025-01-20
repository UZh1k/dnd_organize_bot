from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from src.handlers.game_registration.accept_city import GameRegistrationAcceptCity
from src.handlers.game_registration.states import GameRegistrationStates
from src.models import User
from src.utils.form.form_choice_item import FormChoiceItem


class GameRegistrationAcceptOffline(FormChoiceItem):
    state = GameRegistrationStates.accept_offline
    prepare_text = (
        "Я тебя предупреждаю, что реальный мир может быть также опасен, "
        "как и мир НРИ. Пожалуйста, не собирайся на игры, если их проводят "
        "дома и сам не приглашай никого к себе домой. Можно собираться только "
        "в публичных местах или в онлайне. Это очень важно!"
    )
    form_item_name = "accept_offline"

    alert_message = None
    choices = (("Я понял", "Ok"),)

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        await GameRegistrationAcceptCity.prepare(
            chat_id, user, session, bot, state, self.form_prefix
        )
