from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from controllers.game import GameController
from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    ReviewMenuChoices,
    RATE_STAGE,
)
from models import User, ReviewReceiverTypeEnum
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup
from utils.other import generate_simple_choices


class ReviewRateHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.startswith(
                    f"{REVIEW_CALLBACK_PREFIX}:{ReviewMenuChoices.review_player.value}"
                )
                or call.data.startswith(
                    f"{REVIEW_CALLBACK_PREFIX}:{ReviewMenuChoices.review_dm.value}"
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
        if call.data.startswith(
            f"{REVIEW_CALLBACK_PREFIX}:{ReviewMenuChoices.review_player.value}"
        ):
            await state.add_data(
                receiver_type=ReviewReceiverTypeEnum.player.value,
                to_user_id=int(call.data.split(":")[-1]),
            )
        else:
            game_id = int(call.data.split(":")[-1])
            game = await GameController.get_one(game_id, session)
            await state.add_data(
                receiver_type=ReviewReceiverTypeEnum.dm.value,
                to_user_id=game.creator_id,
            )

        await state.add_data(from_user_id=user.id)

        markup = create_markup(
            (("⭐️", 1), ("⭐️⭐️", 2), ("⭐️⭐️⭐️", 3), ("⭐️⭐️⭐️⭐️", 4), ("⭐️⭐️⭐️⭐️⭐️", 5)),
            RATE_STAGE,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )
        await self.bot.send_message(
            call.message.chat.id,
            "Выбери оценку от 1 до 5",
            reply_markup=markup,
        )
