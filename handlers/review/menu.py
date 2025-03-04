from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.review.settings import ReviewMenuChoices, REVIEW_MENU_PREFIX, \
    REVIEW_CALLBACK_PREFIX
from models import User
from utils.handlers.base_message_handler import BaseMessageHandler
from utils.message_helpers import create_markup


class ReviewMenuHandler(BaseMessageHandler):
    def register_handler(self):
        self.bot.register_message_handler(
            self.handle_message,
            commands=["reviews"],
            chat_types=["private"],
        )

    async def handle_message(
        self,
        message: Message,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        if not user.registered:
            await self.bot.send_message(
                message.chat.id,
                "Не узнаю тебя. Ты точно зарегистрировался? Нажми /register",
            )
            return

        keyboard = create_markup(
            (
                ("Оставить отзыв игроку", ReviewMenuChoices.review_player.value),
                ("Оставить отзыв мастеру", ReviewMenuChoices.review_dm.value),
                ("Посмотреть отзывы на себя", ReviewMenuChoices.review_dm.value),
            ),
            REVIEW_MENU_PREFIX,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )

        await self.bot.send_message(
            message.chat.id,
            "Ты хочешь оставить кому-то отзыв или посмотреть свои оценки?",
            reply_markup=keyboard,
        )
