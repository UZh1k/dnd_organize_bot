from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.review import ReviewController
from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    REVIEW_MENU_PREFIX,
    ReviewMenuChoices,
)
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import generate_review_text, create_markup


class ReadReviewHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.startswith(
                    f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}"
                    f":{ReviewMenuChoices.reviews_about_me.value}"
                )
            ),
        )

    async def on_action(
            self,
            call: CallbackQuery,
            session: AsyncSession,
            user: User,
            state: StateContext,
    ):
        pass

    async def handle_callback(
            self,
            call: CallbackQuery,
            session: AsyncSession,
            user: User,
            state: StateContext,
    ):
        review_num = int(call.data.split(":")[-1])
        reviews = await ReviewController.get_user_reviews(user.id, session)

        if not reviews:
            await self.bot.edit_message_text(
                "Пока нет отзывов", call.message.chat.id, call.message.id
            )
            return

        buttons = []
        if review_num != 0:
            buttons.append(
                (
                    "Предыдущий",
                    f"{ReviewMenuChoices.reviews_about_me.value}:{review_num-1}",
                )
            )
        if review_num != len(reviews) - 1:
            buttons.append(
                (
                    "Следующий",
                    f"{ReviewMenuChoices.reviews_about_me.value}:{review_num+1}",
                )
            )

        keyboard = create_markup(
            buttons,
            REVIEW_MENU_PREFIX,
            row_width=2,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )

        review = reviews[review_num]
        review_text = generate_review_text(review, review_num, len(reviews))
        await self.bot.edit_message_text(
            review_text,
            call.message.chat.id,
            call.message.id,
            reply_markup=keyboard,
        )
