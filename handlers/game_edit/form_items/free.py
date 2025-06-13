from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.game_edit.form_items.about_price import GameEditAboutPrice
from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationFree
from models import User


class GameEditFree(GameRegistrationFree):
    state = GameEditStates.free

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
        if answer == "for_pay":
            await GameEditAboutPrice.prepare(
                chat_id, user, session, bot, state, self.form_prefix
            )
        else:
            await state.add_data(about_price=None)
            await self.next_step(
                chat_id, user, session, bot, state, self.form_prefix, **kwargs
            )
