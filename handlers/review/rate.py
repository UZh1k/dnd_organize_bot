from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    ReviewMenuChoices,
    RATE_STAGE,
    ReviewStates,
)
from controllers.game import GameController
from models import User, ReviewReceiverTypeEnum
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup


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
            receiver_type = ReviewReceiverTypeEnum.player.value
        else:
            receiver_type = ReviewReceiverTypeEnum.dm.value

        to_user_id = int(call.data.split(":")[-1])
        game = await GameController.get_game_for_review(
            user.id,
            to_user_id,
            ReviewReceiverTypeEnum(receiver_type),
            session,
        )
        if not game:
            await self.bot.send_message(call.message.chat.id, "Игра не найдена.")
            return

        next_state = (
            ReviewStates.review
            if game.done is True
            else ReviewStates.write_comment
        )
        await state.delete()
        await state.set(next_state)
        await state.add_data(
            receiver_type=receiver_type,
            to_user_id=to_user_id,
            from_user_id=user.id,
        )

        if game.done is not True:
            await self.bot.edit_message_text(
                "Игра ещё не завершена, поэтому пока можно оставить только комментарий. Напиши его следующим сообщением.",
                call.message.chat.id,
                message_id=call.message.id,
            )
            return

        markup = create_markup(
            (
                ("⭐️", 1),
                ("⭐️⭐️", 2),
                ("⭐️⭐️⭐️", 3),
                ("⭐️⭐️⭐️⭐️", 4),
                ("⭐️⭐️⭐️⭐️⭐️", 5),
            ),
            RATE_STAGE,
            form_prefix=REVIEW_CALLBACK_PREFIX,
        )
        await self.bot.edit_message_text(
            "Выбери оценку от 1 до 5",
            call.message.chat.id,
            message_id=call.message.id,
            reply_markup=markup,
        )
