from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.filters.form_items.filter_item import FilterItem
from handlers.filters.settings import FiltersStates
from handlers.game_registration import GameRegistrationDndRedaction
from models import User


class GameFilterDndRedaction(FilterItem, GameRegistrationDndRedaction):
    state = FiltersStates.dnd_redaction
    prepare_text = "По какой редакции DnD ищешь игру? Выбери из списка."
    set_field = "redaction"

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
        dnd_redaction = set_filters.get("redaction")
        return f"{name}: {dnd_redaction}" if dnd_redaction else name

    async def on_clean(self, state: StateContext):
        await state.add_data(redaction=None)
