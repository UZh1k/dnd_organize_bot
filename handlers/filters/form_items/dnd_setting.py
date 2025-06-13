from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext

from handlers.filters.form_items.filter_item import FilterItem
from handlers.filters.settings import FiltersStates
from handlers.game_registration import GameRegistrationDndSetting
from models import User


class GameFilterDndSetting(FilterItem, GameRegistrationDndSetting):
    state = FiltersStates.dnd_setting
    prepare_text = (
        "В каком сеттинге DnD будет игра? Выбери из списка или "
        "напиши ответ в текстовом сообщении."
    )
    set_field = "setting"

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
        dnd_setting = set_filters.get("setting")
        return f"{name}: {dnd_setting}" if dnd_setting else name

    async def on_clean(self, state: StateContext):
        await state.add_data(setting=None)
