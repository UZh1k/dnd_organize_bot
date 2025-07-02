from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from controllers.review import ReviewController
from handlers.review.settings import (
    ReviewMenuChoices,
    REVIEW_MENU_PREFIX,
    REVIEW_CALLBACK_PREFIX,
)
from models import User, ReviewReceiverTypeEnum
from utils.handlers.base_message_handler import BaseMessageHandler
from utils.message_helpers import create_markup, review_statistic_text


class ReviewMenuHandler(BaseMessageHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            commands=["review"],
            chat_types=["private"],
        )

    async def handle_message(
        self,
        message: Message,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        await state.delete()

        if not user.registered:
            await self.bot.send_message(
                message.chat.id,
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
            ("Оставить отзыв игроку", ReviewMenuChoices.review_player.value),
            ("Оставить отзыв мастеру", ReviewMenuChoices.review_dm.value),
        ]

        if (
            dm_reviews_statistic.comments_count
            or player_reviews_statistic.comments_count
        ):
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

        await self.bot.send_message(
            message.chat.id,
            "Моя статистика: \n\n"
            f"Как мастер: {review_statistic_text(dm_reviews_statistic)}\n"
            f"Как игрок: {review_statistic_text(player_reviews_statistic)}\n\n"
            "Ты хочешь оставить кому-то отзыв или посмотреть свои оценки?",
            reply_markup=keyboard,
        )
