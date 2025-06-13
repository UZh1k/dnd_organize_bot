from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.filters.form_items.filter_item import FilterItem
from handlers.filters.settings import FiltersStates
from handlers.game_registration import GameRegistrationFree
from models import User


class GameFilterFree(FilterItem, GameRegistrationFree):
    state = FiltersStates.free
    prepare_text = "Ищешь бесплатную игру или за деньги?"
    set_field = "free"

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        **kwargs,
    ):
        # todo use super()
        await self.next_step(
            chat_id, user, session, bot, state, self.form_prefix, **kwargs
        )

    @classmethod
    async def prepare_answer(
        cls, name: str, set_filters: dict[str, Any], session: AsyncSession
    ) -> str:
        free = set_filters.get("free")
        return (
            f"{name}: {"Платно" if not free else "Бесплатно"}"
            if free is not None
            else name
        )

    async def on_clean(self, state: StateContext):
        await state.add_data(free=None)
