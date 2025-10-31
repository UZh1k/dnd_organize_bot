from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.review import ReviewController
from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    REVIEW_ITEM_PREFIX,
    ReviewItemMenuChoices,
)
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup


class ReviewItemDeleteClarifyHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.startswith(
                    f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_ITEM_PREFIX}:{ReviewItemMenuChoices.delete_clarify.value}"
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
        review_id = int(call.data.split(":")[-1])
        review = await ReviewController.get_one(review_id, session)

        if not review:
            await self.bot.send_message(
                call.message.chat.id, "Не получилось найти отзыв :("
            )
            return

        keyboard_choices = [
            (
                "Да, удалить",
                f"{ReviewItemMenuChoices.delete.value}:{review.id}",
            ),
            ("Нет, назад", review_id),
        ]
        keyboard = create_markup(
            keyboard_choices,
            REVIEW_ITEM_PREFIX,
            row_width=2,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )

        await self.bot.edit_message_text(
            "Ты уверен, что хочешь удалить отзыв?",
            call.message.chat.id,
            message_id=call.message.id,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
