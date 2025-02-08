from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from handlers.game_edit.settings import GAME_EDIT_FORM_PREFIX, GameEditActions
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler


class CancelEditHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.split(":")[0] == GAME_EDIT_FORM_PREFIX
                and call.data.split(":")[-1] == GameEditActions.cancel.value
            ),
        )

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        await state.delete()
