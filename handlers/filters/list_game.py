from sqlalchemy.ext.asyncio import AsyncSession
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InputMediaPhoto,
    InlineKeyboardMarkup,
)

from controllers.game import GameController
from controllers.game_member import GameMemberController
from handlers.filters.settings import FILTERS_FORM_PREFIX, FiltersStages
from handlers.game_application import GAME_APPLICATION_CALLBACK_PREFIX
from models import User
from utils.game_text import create_game_text, create_game_markup_text
from utils.handlers.base_callback_handler import BaseCallbackHandler


class FiltersListGameHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.startswith(
                    f"{FILTERS_FORM_PREFIX}:{FiltersStages.search.value}"
                )
            ),
        )

    async def check_callback_not_processed(self, call: CallbackQuery) -> bool:
        try:
            if len(call.data.split(":")) == 2:
                await self.bot.edit_message_reply_markup(
                    call.message.chat.id, call.message.message_id, reply_markup=None
                )
            return True
        except ApiTelegramException:
            return False

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        search_number = 0
        call_data_split = call.data.split(":")

        is_first_message = len(call_data_split) == 2
        if not is_first_message:
            search_number = int(call_data_split[-1])

        set_filters = user.filters
        tags = []
        if "tags" in set_filters:
            tags = set_filters.pop("tags") or []

        game, count = await GameController.search_one(
            session, search_number, tags=tags, **set_filters
        )

        back_button = InlineKeyboardButton(
            "Вернуться к фильтрам",
            callback_data=f"{FILTERS_FORM_PREFIX}:{FiltersStages.menu.value}",
        )

        if game is None:
            markup = InlineKeyboardMarkup()
            markup.add(back_button)
            await self.bot.send_message(
                call.message.chat.id,
                "По заданным фильтрам не нашлось игр. Попробуй их немного изменить.",
                reply_markup=markup,
            )
            return

        buttons = []
        if search_number != 0:
            buttons.append(
                ("Предыдущая", f"{FILTERS_FORM_PREFIX}:search:{search_number - 1}")
            )
        if search_number < count - 1:
            buttons.append(
                ("Следующая", f"{FILTERS_FORM_PREFIX}:search:{search_number + 1}")
            )

        players_count = await GameMemberController.count_game_members(game.id, session)
        game_text = create_game_text(game, players_count=players_count)
        game_markup = InlineKeyboardMarkup()
        game_markup_text = await create_game_markup_text(game, session)

        game_markup.row(
            InlineKeyboardButton(
                game_markup_text,
                callback_data=f"{GAME_APPLICATION_CALLBACK_PREFIX}:apply:{game.id}",
            )
        )

        if buttons:
            game_markup.row(
                *[
                    InlineKeyboardButton(name, callback_data=call_data)
                    for name, call_data in buttons
                ]
            )

        game_markup.row(back_button)

        if is_first_message:
            await self.bot.send_photo(
                call.message.chat.id,
                game.image,
                game_text,
                reply_markup=game_markup,
                parse_mode="Markdown",
            )
        else:
            await self.bot.edit_message_media(
                InputMediaPhoto(game.image, game_text, parse_mode="Markdown"),
                call.message.chat.id,
                call.message.id,
                reply_markup=game_markup,
            )
