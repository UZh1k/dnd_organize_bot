from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.game_edit.form_items.accept_city import GameEditAcceptCity
from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationAcceptOffline
from models import User


class GameEditAcceptOffline(GameRegistrationAcceptOffline):
    state = GameEditStates.accept_offline

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        **kwargs
    ):
        await GameEditAcceptCity.prepare(
            chat_id, user, session, bot, state, self.form_prefix
        )
