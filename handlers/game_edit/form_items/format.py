from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.game_edit.form_items.accept_offline import GameEditAcceptOffline
from handlers.game_edit.form_items.platform import GameEditPlatform
from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationFormat
from models import User


class GameEditFormat(GameRegistrationFormat):
    state = GameEditStates.format

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
        if answer == "offline":
            await state.add_data(platform=None)
            await GameEditAcceptOffline.prepare(
                chat_id, user, session, bot, state, self.form_prefix
            )
        elif answer == "online":
            await state.add_data(city_id=None)
            await GameEditPlatform.prepare(
                chat_id, user, session, bot, state, self.form_prefix
            )
        else:
            await state.add_data(city_id=None, platform=None)
            await self.next_step(
                chat_id, user, session, bot, state, self.form_prefix, **kwargs
            )
