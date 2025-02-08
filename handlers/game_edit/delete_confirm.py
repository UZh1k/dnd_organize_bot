from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.game import GameController
from handlers.game_edit.settings import (
    GAME_EDIT_FORM_PREFIX,
    GameEditCallbackPrefixes,
    GameEditActions,
)
from handlers.group_administration.group_funcs import on_close_game
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler


class DeleteConfirmGameHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: call.data
            == (
                f"{GAME_EDIT_FORM_PREFIX}:"
                f"{GameEditCallbackPrefixes.game_action.value}:"
                f"{GameEditActions.delete_confirm.value}"
            ),
        )

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        async with state.data() as data:
            game = await GameController.get_one(data["game_id"], session)
            if not game.done:
                await on_close_game(self.bot, game, session)
        await self.bot.send_message(
            call.message.chat.id,
            "Твоя игра была удалена. Для создания новой игры выбери в "
            "меню “Создание игры” или отправь команду /create.",
        )
        await state.delete()
