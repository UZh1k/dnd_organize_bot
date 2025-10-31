from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from controllers.game_tag import GameTagController
from handlers.filters.form_items.filter_item import FilterItem
from handlers.filters.settings import FiltersStates
from handlers.game_registration import GameRegistrationTag
from models import User


class GameFilterTag(FilterItem, GameRegistrationTag):
    state = FiltersStates.tags
    set_field = "tags"

    @classmethod
    async def prepare_answer(
        cls, name: str, set_filters: dict[str, Any], session: AsyncSession
    ) -> str:
        tags = set_filters.get("tags", [])
        if not tags:
            return name

        tag_objects = await GameTagController.get_list(session, ids=tags)
        return f"{name}: {", ".join([tag.title for tag in tag_objects])}"

    async def on_clean(self, state: StateContext):
        await state.add_data(tags=None)

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
        await self._update_user_filters(user, session, state)
        await super().on_answered(answer, chat_id, user, session, bot, state, **kwargs)
