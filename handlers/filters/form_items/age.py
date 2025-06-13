from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.filters.form_items.filter_item import FilterItem
from handlers.filters.settings import FiltersStates
from handlers.game_registration import GameRegistrationPlayersAge


class GameFilterPlayersAge(FilterItem, GameRegistrationPlayersAge):
    state = FiltersStates.age
    set_field = "min_age"

    @classmethod
    async def prepare_answer(
        cls, name: str, set_filters: dict[str, Any], session: AsyncSession
    ) -> str:
        min_age = set_filters.get("min_age")
        max_age = set_filters.get("max_age")

        if not min_age:
            return name

        players_age = f"{min_age}-{max_age}" if max_age else f"{min_age}+"
        return f"{name}: {players_age}"

    async def on_clean(self, state: StateContext):
        await state.add_data(min_age=None, max_age=None)
