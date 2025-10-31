from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message, CallbackQuery

from controllers.review import ReviewController
from handlers.review.settings import (
    ReviewMenuChoices,
    REVIEW_MENU_PREFIX,
    REVIEW_CALLBACK_PREFIX,
)
from models import User, ReviewReceiverTypeEnum
from utils.handlers.base_handler import BaseHandler
from utils.message_helpers import create_markup, review_statistic_text


class ReviewMenuHandler(BaseHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            commands=["review"],
            chat_types=["private"],
        )
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data
                == f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.menu.value}"
            ),
        )

    async def show_menu(
        self,
        chat_id: int,
        session: AsyncSession,
        user: User,
        state: StateContext,
        edit_message_id: int | None = None,
    ):
        await state.delete()

        if not user.registered:
            await self.bot.send_message(
                chat_id,
                "Не узнаю тебя. Ты точно зарегистрировался? Нажми /register",
            )
            return

        dm_reviews_statistic = await ReviewController.get_reviews_statistic(
            user.id, session, ReviewReceiverTypeEnum.dm.value
        )
        player_reviews_statistic = await ReviewController.get_reviews_statistic(
            user.id, session, ReviewReceiverTypeEnum.player.value
        )

        keyboard_choices = [
            ("Создать новый отзыв", ReviewMenuChoices.create_review.value),
            ("Редактировать существующий отзыв", ReviewMenuChoices.edit_review.value),
        ]

        if dm_reviews_statistic.total_count or player_reviews_statistic.total_count:
            keyboard_choices.append(
                (
                    "Посмотреть отзывы на себя",
                    f"{ReviewMenuChoices.reviews_about_me.value}:0",
                )
            )

        keyboard = create_markup(
            keyboard_choices,
            REVIEW_MENU_PREFIX,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )

        text = (
            "Моя статистика: \n\n"
            f"Как мастер: {review_statistic_text(dm_reviews_statistic)}\n"
            f"Как игрок: {review_statistic_text(player_reviews_statistic)}\n\n"
            "Ты хочешь оставить новый отзыв, исправить существующий"
            " или посмотреть свои оценки?"
        )
        if edit_message_id:
            await self.bot.edit_message_text(
                text,
                chat_id,
                message_id=edit_message_id,
                reply_markup=keyboard,
            )
        else:
            await self.bot.send_message(
                chat_id,
                text,
                reply_markup=keyboard,
            )

    async def handle_message(
        self,
        message: Message,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        await self.show_menu(message.chat.id, session, user, state)

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        await self.show_menu(
            call.message.chat.id, session, user, state, edit_message_id=call.message.id
        )
