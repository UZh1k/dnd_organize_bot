from sqlalchemy.ext.asyncio import AsyncSession
from telebot.apihelper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.game import GameController
from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    REVIEW_MENU_PREFIX,
    ReviewMenuChoices,
)
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup, get_pagination_row


class ReviewChooseGameHandler(BaseCallbackHandler):
    page_size = 10

    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: call.data.startswith(
                f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.review_dm.value}"
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

        games, total_count = await GameController.get_games_to_review(
            user.id, session, self.page_size, page
        )

        if not games:
            markup = create_markup(
                (("Назад", ReviewMenuChoices.menu.value),),
                REVIEW_MENU_PREFIX,
                form_prefix=REVIEW_CALLBACK_PREFIX,
            )
            await self.bot.edit_message_text(
                "Похоже, что ты уже оценил всех мастеров, с кем играл, "
                "или вышел из группы с уже прошедшей игрой. "
                "Чтобы сохранить возможность оценить сопартийцев или мастера игры, "
                "не выходи из чата вашего завершенного приключения.",
                call.message.chat.id,
                message_id=call.message.id,
                reply_markup=markup,
            )
            return

        markup = create_markup(
            tuple(
                (f"{game.title} от мастера {game.creator.name}", game.creator_id)
                for game in games
            ),
            ReviewMenuChoices.review_dm.value,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )
        markup.add(
            *get_pagination_row(
                page,
                total_count,
                self.page_size,
                f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.review_dm.value}",
            ),
            row_width=2,
        )

        if first_message:
            await self.bot.edit_message_text(
                "Выбери игру, мастера которой хочешь оценить.",
                call.message.chat.id,
                message_id=call.message.id,
                reply_markup=markup,
            )
        else:
            await self.bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=markup
            )
