from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.filters.form_items.city import GameFilterCity
from handlers.filters.form_items.filter_item import FilterItem
from handlers.filters.settings import FiltersStates
from handlers.game_registration import GameRegistrationFormat
from models import User, GameFormatText, GameFormat


class GameFilterFormat(FilterItem, GameRegistrationFormat):
    state = FiltersStates.format
    prepare_text = "В каком формате ищешь игру?"
    set_field = "format"

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        if text != "online":
            await state.add_data(platform=None)
        if text != "offline":
            await state.add_data(city_id=None)
        await super().save_answer(text, user, session, state)

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        edit_message_id: int = None,
        **kwargs,
    ):
        if answer == "offline":
            await GameFilterCity.prepare(
                chat_id,
                user,
                session,
                bot,
                state,
                self.form_prefix,
                edit_message_id=edit_message_id,
            )
        else:
            await self.next_step(
                chat_id,
                user,
                session,
                bot,
                state,
                self.form_prefix,
                edit_message_id=edit_message_id,
                **kwargs,
            )

    @classmethod
    async def prepare_answer(
        cls, name: str, set_filters: dict[str, Any], session: AsyncSession
    ) -> str:
        game_format = set_filters.get("format")
        return (
            f"{name}: {GameFormatText[GameFormat(game_format).name].value}"
            if game_format
            else name
        )

    async def on_clean(self, state: StateContext):
        await state.add_data(format=None, city_id=None)
