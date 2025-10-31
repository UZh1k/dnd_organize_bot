from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.review import ReviewController
from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    REVIEW_ITEM_PREFIX,
    ReviewMenuChoices,
    REVIEW_MENU_PREFIX,
    ReviewItemMenuChoices,
)
from models import User, ReviewReceiverTypeEnum
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup


class ReviewItemHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.startswith(f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_ITEM_PREFIX}:")
            ),
        )

    @classmethod
    async def show_menu(
        cls,
        chat_id: int,
        review_id: int,
        session: AsyncSession,
        user: User,
        bot: AsyncTeleBot,
        edit_message_id: int | None = None,
    ):
        review = await ReviewController.get_one(review_id, session)

        if not review:
            await bot.send_message(chat_id, "Не получилось найти отзыв :(")
            return

        review_menu_step = (
            ReviewMenuChoices.review_player.value
            if review.receiver_type == ReviewReceiverTypeEnum.player
            else ReviewMenuChoices.review_dm.value
        )

        keyboard_choices = [
            ("⬅️ Назад", f"{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.edit_review.value}"),
            ("✏️ Редактировать", f"{review_menu_step}:{review.to_user_id}"),
            (
                "🗑 Удалить",
                f"{REVIEW_ITEM_PREFIX}:{ReviewItemMenuChoices.delete_clarify.value}:{review.id}",
            ),
            ("✅ Ок", f"{REVIEW_ITEM_PREFIX}:{ReviewItemMenuChoices.ok.value}"),
        ]

        keyboard = create_markup(keyboard_choices, REVIEW_CALLBACK_PREFIX)

        prefix = (
            "игроку"
            if review.receiver_type == ReviewReceiverTypeEnum.player
            else "мастеру"
        )
        comment = f"Комментарий: {review.comment}\n\n" if review.comment else "\n"

        text = (
            f"*Отзыв {prefix} {review.to_user.name}*\n\n"
            f"Оценка: {review.value}⭐️\n"
            f"{comment}"
            f"Что ты хочешь сделать с отзывом?"
        )
        if edit_message_id:
            await bot.edit_message_text(
                text,
                chat_id,
                message_id=edit_message_id,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
        else:
            await bot.send_message(
                chat_id,
                text,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        review_id = int(call.data.split(":")[-1])
        await self.show_menu(
            call.message.chat.id,
            review_id,
            session,
            user,
            self.bot,
            edit_message_id=call.message.id,
        )
