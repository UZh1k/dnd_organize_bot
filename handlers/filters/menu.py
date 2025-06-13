from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from handlers.filters.prepare_question import FILTER_OPTION_HANDLER_MAP
from handlers.filters.settings import (
    FiltersStates,
    FilterOptions,
    FILTERS_FORM_PREFIX,
    FiltersStages,
)
from models import User, GameFormat
from utils.handlers.base_handler import BaseHandler
from utils.message_helpers import get_channel_link


class FiltersMenuHandler(BaseHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            commands=["search"],
            chat_types=["private"],
        )
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: call.data
            == (f"{FILTERS_FORM_PREFIX}:" f"{FiltersStages.menu.value}"),
        )

    @classmethod
    async def show_menu(
        cls,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        edit_message_id: int | None = None,
    ):
        await state.set(FiltersStates.menu)

        set_filters = {}
        async with state.data() as data:
            set_filters = data

        keyboard = InlineKeyboardMarkup()

        if set_filters.get("format") == GameFormat.offline.value:
            first_row = (
                ("Формат", FilterOptions.format.value),
                ("Город", FilterOptions.city.value),
            )
        else:
            first_row = (("Формат", FilterOptions.format.value),)

        markup = (
            first_row,
            (
                ("Цена", FilterOptions.free.value),
                ("Игровая система", FilterOptions.system.value),
            ),
        )

        if set_filters.get("system") == "DnD":
            markup += (
                (
                    ("Редакция", FilterOptions.dnd_redaction.value),
                    ("Сеттинг", FilterOptions.dnd_setting.value),
                ),
            )

        markup += (
            (
                ("Тип игры", FilterOptions.game_type.value),
                ("Возраст", FilterOptions.age.value),
            ),
            (("Тэги", FilterOptions.tags.value),),
        )

        for row in markup:
            keyboard.row(
                *[
                    InlineKeyboardButton(
                        (
                            await FILTER_OPTION_HANDLER_MAP[call_data].prepare_answer(
                                name, set_filters, session
                            )
                        ),
                        callback_data=(
                            f"{FILTERS_FORM_PREFIX}:"
                            f"{FiltersStages.choose_filter.value}:"
                            f"{call_data}"
                        ),
                    )
                    for name, call_data in row
                ]
            )

        keyboard.row(
            InlineKeyboardButton(
                "🗑 Очистить фильтры",
                callback_data=(
                    f"{FILTERS_FORM_PREFIX}:{FiltersStages.clear_filters.value}"
                ),
            )
        )
        keyboard.row(
            InlineKeyboardButton(
                "🔎 Поиск по фильтрам",
                callback_data=f"{FILTERS_FORM_PREFIX}:{FiltersStages.search.value}",
            )
        )

        channel_link = await get_channel_link(bot)
        text = (
            '*Фильтры*\n\n'
            'Добавь фильтры и нажми кнопку "Поиск по фильтрам".\n\n'
            f'Также все игры можно посмотреть в нашем [канале]({channel_link}), '
            f'обязательно подписывайся!'
        )
        if edit_message_id:
            try:
                await bot.edit_message_text(
                    text,
                    chat_id,
                    edit_message_id,
                    reply_markup=keyboard,
                    parse_mode="Markdown",
                )
            except ApiTelegramException:
                pass
        else:
            await bot.send_message(
                chat_id,
                text,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

    async def handle_message(
        self,
        message: Message,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        await self.show_menu(message.chat.id, user, session, self.bot, state)

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        await self.show_menu(call.message.chat.id, user, session, self.bot, state)
