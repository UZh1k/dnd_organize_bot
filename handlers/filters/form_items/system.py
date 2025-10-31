from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.filters.form_items.filter_item import FilterItem
from handlers.filters.settings import FiltersStates
from handlers.game_registration import GameRegistrationSystem
from models import User


class GameFilterSystem(FilterItem, GameRegistrationSystem):
    state = FiltersStates.system
    prepare_text = "Выбери из списка или напиши текстом игровую систему."
    set_field = "system"

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        if text != "DnD":
            await state.add_data(redaction=None, setting=None)
        await super().save_answer(text, user, session, state)

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
        system = set_filters.get("system")
        return f"{name}: {system}" if system else name

    async def on_clean(self, state: StateContext):
        await state.add_data(system=None, redaction=None, setting=None)
