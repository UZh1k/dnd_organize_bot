from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from handlers.filters.form_items.filter_item import FilterItem
from handlers.filters.settings import FiltersStates
from handlers.game_registration import GameRegistrationPlatform


class GameFilterPlatform(FilterItem, GameRegistrationPlatform):
    state = FiltersStates.platform
    prepare_text = (
        "На какой онлайн площадке ищешь игру? Выбери из списка или введи название."
    )
    set_field = "platform"

    @classmethod
    async def prepare_answer(
        cls, name: str, set_filters: dict[str, Any], session: AsyncSession
    ) -> str:
        platform = set_filters.get("platform")
        return f"{name}: {platform}" if platform else name

    async def on_clean(self, state: StateContext):
        await state.add_data(platform=None)
