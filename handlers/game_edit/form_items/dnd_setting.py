from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationDndSetting
from models import User


class GameEditDndSetting(GameRegistrationDndSetting):
    state = GameEditStates.dnd_setting

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
        # todo use super()
        await self.next_step(
            chat_id, user, session, bot, state, self.form_prefix, **kwargs
        )
