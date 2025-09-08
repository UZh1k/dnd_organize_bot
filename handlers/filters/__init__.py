from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import (
    Message,
)

from handlers.filters.clean_filters import FiltersCleanHandler
from handlers.filters.form_items import (
    GameFilterPlayersAge,
    GameFilterFormat,
    GameFilterCity,
    GameFilterSystem,
    GameFilterType,
    GameFilterDndSetting,
    GameFilterDndRedaction,
    GameFilterFree,
    GameFilterTag,
    GameFilterPlatform,
)
from handlers.filters.list_game import FiltersListGameHandler
from handlers.filters.menu import FiltersMenuHandler
from handlers.filters.prepare_question import FiltersPrepareQuestionHandler
from handlers.filters.settings import FILTERS_FORM_PREFIX
from models import User
from utils.form.form_item_group import FormItemGroup
from utils.handler_groups.base_handler_group import BaseHandlerGroup
from utils.handler_groups.registration_handler_group import RegistrationHandlerGroup


class FiltersHandlerGroup(RegistrationHandlerGroup):
    handlers = [
        FiltersMenuHandler,
        FiltersListGameHandler,
        FiltersPrepareQuestionHandler,
        FiltersCleanHandler,
    ]
    form_item_groups: tuple[FormItemGroup] = (
        FormItemGroup(main=GameFilterPlayersAge),
        FormItemGroup(
            main=GameFilterFormat,
            side=(GameFilterCity,),
        ),
        FormItemGroup(main=GameFilterPlatform),
        FormItemGroup(main=GameFilterSystem),
        FormItemGroup(main=GameFilterDndSetting),
        FormItemGroup(main=GameFilterDndRedaction),
        FormItemGroup(main=GameFilterType),
        FormItemGroup(main=GameFilterFree),
        FormItemGroup(main=GameFilterTag),
    )
    command: str = "search"
    form_prefix: str = FILTERS_FORM_PREFIX

    async def first_step(
        self,
        message: Message,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        await FiltersMenuHandler.show_menu(message.chat.id, user, session, bot, state)

    async def last_step(
        self,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        form_prefix: str,
        edit_message_id: int = None,
        **kwargs,
    ):
        await FiltersMenuHandler.show_menu(
            chat_id, user, session, bot, state, edit_message_id=edit_message_id
        )

    def register_handlers(self):
        BaseHandlerGroup.register_handlers(self)

        for current_item_group in self.form_item_groups:

            for current_item in (current_item_group.main, *current_item_group.side):
                self.register_form_handlers(
                    current_item(self.last_step, self.form_prefix)
                )
