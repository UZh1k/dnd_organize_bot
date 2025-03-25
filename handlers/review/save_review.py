from sqlalchemy.ext.asyncio import AsyncSession
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery, Message

from consts import NEWS_CHANNEL_ID
from controllers.game import GameController
from controllers.review import ReviewController
from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    EMPTY_CALLBACK,
    ReviewStates,
)
from models import User, ReviewReceiverTypeEnum, Game
from utils.game_text import create_game_markup
from utils.handlers.base_handler import BaseHandler


class SaveReviewHandler(BaseHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data == f"{REVIEW_CALLBACK_PREFIX}:{EMPTY_CALLBACK}"
            ),
        )
        self.bot.register_message_handler(
            self.handle_message,
            state=ReviewStates.write_comment,
            chat_types=["private"],
        )

    async def save_review(
        self,
        chat_id: int,
        session: AsyncSession,
        state: StateContext,
        comment: str | None = None,
    ):
        async with state.data() as data:
            review_data = data

        review_data["comment"] = comment
        if "game_id" in review_data:
            del review_data["game_id"]
        await ReviewController.create(review_data, session)

        await self.bot.send_message(chat_id, "Отзыв сохранен")
        await state.delete()

        if review_data["receiver_type"] == ReviewReceiverTypeEnum.dm.value:
            dm_id = review_data["to_user_id"]
            dm_active_games = await GameController.get_list(
                session, Game.creator_id == dm_id, Game.active.is_(True)
            )
            for game in dm_active_games:
                markup = await create_game_markup(game, session)
                try:
                    await self.bot.edit_message_reply_markup(
                        NEWS_CHANNEL_ID, game.post_id, reply_markup=markup
                    )
                except ApiTelegramException:
                    pass

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        if len(message.text) > 1000:
            await self.bot.send_message(message.chat.id, "Слишкой большой текст")
            return
        await self.save_review(message.chat.id, session, state, comment=message.text)

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        await self.save_review(call.message.chat.id, session, state)
