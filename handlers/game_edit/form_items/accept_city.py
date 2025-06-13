from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.game_edit.form_items.city import GameEditCity
from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationAcceptCity
from models import User


class GameEditAcceptCity(GameRegistrationAcceptCity):
    state = GameEditStates.accept_city

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        **kwargs,
    ):
        if answer == "no":
            await GameEditCity.prepare(
                chat_id, user, session, bot, state, self.form_prefix
            )
        else:
            await self.next_step(
                chat_id, user, session, bot, state, self.form_prefix, **kwargs
            )
