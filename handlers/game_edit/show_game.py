from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from handlers.game_edit import GAME_EDIT_FORM_PREFIX, GameEditCallbackPrefixes
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler


class ShowGameHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: call.data.startswith(
                f"{GAME_EDIT_FORM_PREFIX}:{GameEditCallbackPrefixes.choose_game}"
            ),
        )

    def handle_callback(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ): ...
