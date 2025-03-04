from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.user import UserController
from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    REVIEW_MENU_PREFIX,
    ReviewMenuChoices, ReviewStates,
)
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup


class ReviewChooseGameHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data
                == f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.review_player.value}"
            ),
        )

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        players = await UserController.get_players_to_review(user.id, session)

        markup = create_markup(
            tuple((f"{player.name} {player.username}", str(player.id)) for player in players),
            ReviewMenuChoices.review_player.value,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )
        await state.set(ReviewStates.review_player)
        await self.bot.send_message(
            call.message.chat.id,
            "Выбери игрока, которого хочешь оценить.",
            reply_markup=markup,
        )
