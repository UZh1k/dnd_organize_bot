from sqlalchemy.ext.asyncio import AsyncSession
from telebot.apihelper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery, InlineKeyboardButton

from controllers.game import GameController
from handlers.review.settings import (
    REVIEW_MENU_PREFIX,
    ReviewMenuChoices,
    REVIEW_CALLBACK_PREFIX,
    ReviewStates,
)
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup


class ReviewChooseGameHandler(BaseCallbackHandler):
    page_size = 10

    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.startswith(
                    f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.review_dm.value}"
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

        games, total_count = await GameController.get_games_to_review(
            user.id, session, self.page_size, page
        )

        if not games:
            await self.bot.send_message(
                call.message.chat.id,
                "Похоже, что ты уже оценил всех мастеров, с кем играл, "
                "или вышел из группы с уже прошедшей игрой. "
                "Чтобы сохранить возможность оценить сопартийцев или мастера игры, "
                "не выходи из чата вашего завершенного приключения.",
            )
            return

        last_row = []
        is_last_page = (page + 1) * self.page_size >= total_count
        if total_count > self.page_size:
            if page != 0:
                last_row.append(
                    InlineKeyboardButton(
                        f"Предыдущая страница",
                        callback_data=f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.review_dm.value}:{page - 1}",
                    )
                )
            if not is_last_page:
                last_row.append(
                    InlineKeyboardButton(
                        f"Следующая страница",
                        callback_data=f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.review_dm.value}:{page+1}",
                    )
                )

        markup = create_markup(
            tuple(
                (f"{game.title} от мастера {game.creator.name}", str(game.id))
                for game in games
            ),
            ReviewMenuChoices.review_dm.value,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )
        markup.add(*last_row, row_width=2)

        await state.set(ReviewStates.review_dm)

        if first_message:
            await self.bot.send_message(
                call.message.chat.id,
                "Выбери игру, мастера которой хочешь оценить.",
                reply_markup=markup,
            )
        else:
            await self.bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=markup
            )
