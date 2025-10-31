from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.review import ReviewController
from handlers.review.save_review import SaveReviewHandler
from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    REVIEW_ITEM_PREFIX,
    ReviewItemMenuChoices,
)
from models import User, ReviewReceiverTypeEnum
from utils.handlers.base_callback_handler import BaseCallbackHandler


class ReviewItemDeleteHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.startswith(
                    f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_ITEM_PREFIX}:{ReviewItemMenuChoices.delete.value}"
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

        await session.delete(review)
        await self.bot.edit_message_text(
            "Отзыв удален.",
            call.message.chat.id,
            message_id=call.message.id,
        )

        if review.receiver_type == ReviewReceiverTypeEnum.dm:
            await SaveReviewHandler.update_dm_games(
                review.to_user_id, session, self.bot
            )
