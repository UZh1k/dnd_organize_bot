from sqlalchemy.ext.asyncio import AsyncSession
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery, InlineKeyboardButton

from controllers.review import ReviewController
from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    REVIEW_MENU_PREFIX,
    ReviewMenuChoices,
    REVIEW_ITEM_PREFIX,
)
from models import User, ReviewReceiverTypeEnum
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup, get_pagination_row


class MenuEditReviewHandler(BaseCallbackHandler):
    page_size = 10

    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.startswith(
                    f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.edit_review.value}"
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

        reviews, total_count = await ReviewController.get_reviews_from_user(
            user.id, session, self.page_size, page
        )

        keyboard_choices = []

        for review in reviews:
            prefix = (
                "Игрок"
                if review.receiver_type == ReviewReceiverTypeEnum.player
                else "Мастер"
            )
            comment_text = "с комментарием" if review.comment else "без комментария"
            keyboard_choices.append(
                (
                    f"{prefix} {review.to_user.name}: {review.value}⭐️, {comment_text}",
                    review.id,
                )
            )

        keyboard = create_markup(
            keyboard_choices,
            REVIEW_ITEM_PREFIX,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )
        keyboard.add(
            InlineKeyboardButton(
                "Назад",
                callback_data=f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.menu.value}",
            )
        )
        keyboard.add(
            *get_pagination_row(
                page,
                total_count,
                self.page_size,
                f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.edit_review.value}",
            ),
            row_width=2,
        )

        if first_message:
            await self.bot.edit_message_text(
                "Выбери отзыв, который хочешь поменять.",
                call.message.chat.id,
                message_id=call.message.id,
                reply_markup=keyboard,
            )
        else:
            await self.bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=keyboard
            )
