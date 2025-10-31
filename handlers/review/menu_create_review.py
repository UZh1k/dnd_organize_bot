from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    REVIEW_MENU_PREFIX,
    ReviewMenuChoices,
)
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup


class MenuCreateReviewHandler(BaseCallbackHandler):

    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data
                == (
                    f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.create_review.value}"
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

        keyboard_choices = [
            ("Оставить отзыв игроку", ReviewMenuChoices.review_player.value),
            ("Оставить отзыв мастеру", ReviewMenuChoices.review_dm.value),
            ("Назад", ReviewMenuChoices.menu.value),
        ]

        keyboard = create_markup(
            keyboard_choices,
            REVIEW_MENU_PREFIX,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )

        await self.bot.edit_message_text(
            "Выбери, кого ты хочешь оценить.",
            call.message.chat.id,
            message_id=call.message.id,
            reply_markup=keyboard,
        )
