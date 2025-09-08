from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.game import GameController
from handlers.game_edit.settings import (
    GAME_EDIT_FORM_PREFIX,
    GameEditCallbackPrefixes,
    GameEditActions,
    GameEditOptionsStr,
)
from models import User, GameFormat
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup


class GameEditConfirmHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: call.data
            == (
                f"{GAME_EDIT_FORM_PREFIX}:"
                f"{GameEditCallbackPrefixes.game_action.value}:"
                f"{GameEditActions.edit.value}"
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
            if game_id := data.get("game_id"):
                game = await GameController.get_one(game_id, session)
            else:
                return

        edit_options = []
        for option in GameEditOptionsStr:
            if (
                option is GameEditOptionsStr.city
                and game.format != GameFormat.offline
                or (
                    option is GameEditOptionsStr.platform
                    and game.format != GameFormat.online
                )
                or (
                    option is GameEditOptionsStr.redaction_and_setting
                    and game.system == "DnD"
                )
                or (
                    option
                    in (
                        GameEditOptionsStr.dnd_setting,
                        GameEditOptionsStr.dnd_redaction,
                    )
                    and game.system != "DnD"
                )
            ):
                continue
            edit_options.append((option.value, option.name))
        edit_options.append(("Все ОК", GameEditActions.cancel.value))
        markup = create_markup(
            tuple(edit_options),
            GameEditCallbackPrefixes.choose_option.value,
            form_prefix=GAME_EDIT_FORM_PREFIX,
        )

        await self.bot.send_message(
            call.message.chat.id,
            "Выбери, что ты хочешь скорректировать.",
            reply_markup=markup,
        )
