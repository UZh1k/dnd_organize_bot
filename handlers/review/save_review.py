from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery, Message

from consts import NEWS_CHANNEL_ID
from controllers.game import GameController
from controllers.review import ReviewController
from controllers.user import UserController
from handlers.review.review_item import ReviewItemHandler
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

    @classmethod
    async def update_dm_games(
        cls, dm_id: int, session: AsyncSession, bot: AsyncTeleBot
    ):
        dm_active_games = await GameController.get_list(
            session, Game.creator_id == dm_id, Game.active.is_(True)
        )
        for game in dm_active_games:
            markup = await create_game_markup(game, session)
            try:
                await bot.edit_message_reply_markup(
                    NEWS_CHANNEL_ID, game.post_id, reply_markup=markup
                )
            except ApiTelegramException:
                pass

    async def save_review(
        self,
        chat_id: int,
        session: AsyncSession,
        user: User,
        state: StateContext,
        comment: str | None = None,
        edit_message_id: int | None = None,
    ):
        async with state.data() as data:
            review_data = data

        if not await UserController.get_one(review_data["to_user_id"], session):
            await self.bot.send_message(
                chat_id, "Такого пользователя не существует. Попробуй начать сначала."
            )

        review_data["comment"] = comment
        if "game_id" in review_data:
            del review_data["game_id"]

        review = await ReviewController.find_one(
            user.id, review_data["to_user_id"], review_data["receiver_type"], session
        )
        if not review:
            review = await ReviewController.create(review_data, session)
        else:

            if review.unchangeable:
                await self.bot.send_message(
                    chat_id,
                    "Отзыв по какой-то причине отмечен, как не редактируемый. "
                    "За разъяснениями обратись в поддержку.",
                )
                return

            review.value = review_data["value"]
            review.comment = review_data.get("comment")
            await session.flush()

        await state.delete()

        await ReviewItemHandler.show_menu(
            chat_id, review.id, session, user, self.bot, edit_message_id
        )

        if review_data["receiver_type"] == ReviewReceiverTypeEnum.dm.value:
            dm_id = review_data["to_user_id"]
            await self.update_dm_games(dm_id, session, self.bot)

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        if len(message.text) > 1000:
            await self.bot.send_message(message.chat.id, "Слишкой большой текст")
            return
        await self.save_review(
            message.chat.id, session, user, state, comment=message.text
        )

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        await self.save_review(
            call.message.chat.id, session, user, state, edit_message_id=call.message.id
        )
