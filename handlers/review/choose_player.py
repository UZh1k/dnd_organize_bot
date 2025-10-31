from sqlalchemy.ext.asyncio import AsyncSession
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery, InlineKeyboardButton

from controllers.user import UserController
from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    REVIEW_MENU_PREFIX,
    ReviewMenuChoices,
)
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup


class ReviewChoosePlayerHandler(BaseCallbackHandler):
    page_size = 10

    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.startswith(
                    f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.review_player.value}"
                )
            ),
        )

    async def check_callback_not_processed(self, call: CallbackQuery) -> bool:
        try:
            if len(call.data.split(":")) == 3:
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
        call_data_split = call.data.split(":")
        first_message = False
        if len(call_data_split) == 3:
            page = 0
            first_message = True
        else:
            page = int(call_data_split[-1])

        players_and_games, total_count = await UserController.get_players_to_review(
            user.id, session, self.page_size, page
        )

        if not players_and_games:
            markup = create_markup(
                (("Назад", ReviewMenuChoices.menu.value),),
                REVIEW_MENU_PREFIX,
                form_prefix=REVIEW_CALLBACK_PREFIX,
            )
            await self.bot.edit_message_text(
                "Похоже, что ты уже оценил всех игроков, с кем играл, "
                "или вышел из группы с уже прошедшей игрой. "
                "Чтобы сохранить возможность оценить сопартийцев или мастера игры, "
                "не выходи из чата вашего завершенного приключения.",
                call.message.chat.id,
                message_id=call.message.id,
                reply_markup=markup,
            )
            return

        last_row = []
        is_last_page = (page + 1) * self.page_size >= total_count
        if total_count > self.page_size:
            if page != 0:
                last_row.append(
                    InlineKeyboardButton(
                        "Предыдущая страница",
                        callback_data=f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.review_player.value}:{page - 1}",
                    )
                )
            if not is_last_page:
                last_row.append(
                    InlineKeyboardButton(
                        "Следующая страница",
                        callback_data=f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.review_player.value}:{page + 1}",
                    )
                )

        keyboard = []
        for player, game in players_and_games:
            player_text = f"({player.username}) " if player.username else ""
            keyboard.append(
                (
                    (
                        f"{player.name} {player_text} - {game.title}"
                        if player.username
                        else player.name
                    ),
                    str(player.id),
                )
            )

        markup = create_markup(
            keyboard,
            ReviewMenuChoices.review_player.value,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )
        markup.add(*last_row, row_width=2)

        if first_message:
            await self.bot.edit_message_text(
                "Выбери игрока, которого хочешь оценить.",
                call.message.chat.id,
                message_id=call.message.id,
                reply_markup=markup,
            )
        else:
            await self.bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=markup
            )
