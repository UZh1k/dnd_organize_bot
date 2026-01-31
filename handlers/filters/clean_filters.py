from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from handlers.filters.menu import FiltersMenuHandler
from handlers.filters.settings import FILTERS_FORM_PREFIX, FiltersStages

from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler


class FiltersCleanHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: call.data
            == (f"{FILTERS_FORM_PREFIX}:{FiltersStages.clear_filters.value}"),
        )

    async def handle_callback(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        async with state.data() as data:
            set_filters = data
        if set_filters:
            await state.delete()
            user.filters = {}
            await session.flush()
            await FiltersMenuHandler.show_menu(
                call.message.chat.id,
                user,
                session,
                self.bot,
                state,
                edit_message_id=call.message.id,
            )
        else:
            await self.bot.answer_callback_query(call.id, text="Фильтры не заданы")
