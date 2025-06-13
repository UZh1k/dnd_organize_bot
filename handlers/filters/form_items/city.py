from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext

from controllers.city import CityController
from handlers.filters.form_items.filter_item import FilterItem
from handlers.filters.settings import FiltersStates
from handlers.game_registration import GameRegistrationCity


class GameFilterCity(FilterItem, GameRegistrationCity):
    state = FiltersStates.city
    prepare_text = (
        "Выбери город из списка "
        "или напиши текстом название, если нужного города здесь нет."
    )
    set_field = "city_id"

    @classmethod
    async def prepare_answer(
        cls, name: str, set_filters: dict[str, Any], session: AsyncSession
    ) -> str:
        city_id = set_filters.get("city_id")

        if not city_id:
            return name

        city = await CityController.get_one(city_id, session)
        return f"{name}: {city.name}"

    async def on_clean(self, state: StateContext):
        await state.add_data(city_id=None)
