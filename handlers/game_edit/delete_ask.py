from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from handlers.game_edit.settings import (
    GAME_EDIT_FORM_PREFIX,
    GameEditCallbackPrefixes,
    GameEditActions,
)
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup


class DeleteAskGameHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: call.data
            == (
                f"{GAME_EDIT_FORM_PREFIX}:"
                f"{GameEditCallbackPrefixes.game_action.value}:"
                f"{GameEditActions.delete.value}"
            ),
        )

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        markup = create_markup(
            (
                ("Удалить", GameEditActions.delete_confirm.value),
                ("Отмена", GameEditActions.cancel.value),
            ),
            GameEditCallbackPrefixes.game_action.value,
            form_prefix=GAME_EDIT_FORM_PREFIX,
        )
        await self.bot.send_message(
            call.message.chat.id,
            "Ты уверен, что хочешь удалить игру?",
            reply_markup=markup,
        )
