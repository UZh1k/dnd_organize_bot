from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.game import GameController
from handlers.review.settings import (
    REVIEW_MENU_PREFIX,
    ReviewMenuChoices,
    REVIEW_CALLBACK_PREFIX,
    REVIEW_CHOOSE_GAME_PREFIX,
    ReviewStates,
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
                == f"{REVIEW_CALLBACK_PREFIX}:{REVIEW_MENU_PREFIX}:{ReviewMenuChoices.review_dm.value}"
            ),
        )

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        games = await GameController.get_games_to_review(user.id, session)

        markup = create_markup(
            tuple((game.title, str(game.id)) for game in games),
            ReviewMenuChoices.review_dm.value,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )
        await state.set(ReviewStates.review_dm)
        await self.bot.send_message(
            call.message.chat.id,
            "Выбери игру, мастера которой хочешь оценить.",
            reply_markup=markup,
        )
