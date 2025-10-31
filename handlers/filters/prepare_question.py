from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from handlers.filters.form_items import (
    GameFilterPlayersAge,
    GameFilterCity,
    GameFilterDndRedaction,
    GameFilterDndSetting,
    GameFilterFormat,
    GameFilterFree,
    GameFilterType,
    GameFilterSystem,
    GameFilterTag,
    GameFilterPlatform,
)
from handlers.filters.settings import FilterOptions, FILTERS_FORM_PREFIX, FiltersStages
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler

FILTER_OPTION_HANDLER_MAP = {
    FilterOptions.age.value: GameFilterPlayersAge,
    FilterOptions.city.value: GameFilterCity,
    FilterOptions.platform.value: GameFilterPlatform,
    FilterOptions.dnd_redaction.value: GameFilterDndRedaction,
    FilterOptions.dnd_setting.value: GameFilterDndSetting,
    FilterOptions.format.value: GameFilterFormat,
    FilterOptions.free.value: GameFilterFree,
    FilterOptions.game_type.value: GameFilterType,
    FilterOptions.system.value: GameFilterSystem,
    FilterOptions.tags.value: GameFilterTag,
}


class FiltersPrepareQuestionHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: call.data.startswith(
                f"{FILTERS_FORM_PREFIX}:" f"{FiltersStages.choose_filter.value}"
            )
            and call.data.split(":")[-1] in FILTER_OPTION_HANDLER_MAP,
        )

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        question = call.data.split(":")[-1]

        handler = FILTER_OPTION_HANDLER_MAP[question]

        await handler.prepare(
            call.message.chat.id,
            user,
            session,
            self.bot,
            state,
            FILTERS_FORM_PREFIX,
            edit_message_id=call.message.id,
            chosen_tags=user.filters.get("tags") or [],
        )
