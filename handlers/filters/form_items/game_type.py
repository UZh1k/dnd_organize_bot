from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.filters.form_items.filter_item import FilterItem
from handlers.filters.settings import FiltersStates
from handlers.game_registration import GameRegistrationType
from models import GameType, GameTypeText


class GameFilterType(FilterItem, GameRegistrationType):
    state = FiltersStates.game_type
    set_field = "type"

    @classmethod
    async def prepare_answer(
        cls, name: str, set_filters: dict[str, Any], session: AsyncSession
    ) -> str:
        game_type = set_filters.get("type")
        return (
            f"{name}: {GameTypeText[GameType(game_type).name].value}"
            if game_type
            else name
        )

    async def on_clean(self, state: StateContext):
        await state.add_data(type=None)
