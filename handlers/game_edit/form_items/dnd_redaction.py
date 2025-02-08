from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.game_edit.form_items.dnd_setting import GameEditDndSetting
from handlers.game_edit.settings import GameEditStates
from handlers.game_registration import GameRegistrationDndRedaction
from models import User


class GameEditDndRedaction(GameRegistrationDndRedaction):
    state = GameEditStates.dnd_redaction

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        await GameEditDndSetting.prepare(
            chat_id, user, session, bot, state, self.form_prefix
        )
