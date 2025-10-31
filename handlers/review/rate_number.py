from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from handlers.review.settings import (
    REVIEW_CALLBACK_PREFIX,
    RATE_STAGE,
    ReviewStates,
    EMPTY_CALLBACK,
)
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup


class RateNumberHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.startswith(f"{REVIEW_CALLBACK_PREFIX}:{RATE_STAGE}")
            ),
        )

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        rate_number = int(call.data.split(":")[-1])

        keyboard = create_markup(
            (("Сохранить без комментария", EMPTY_CALLBACK),),
            REVIEW_CALLBACK_PREFIX,
        )

        await self.bot.edit_message_text(
            "Отлично! Теперь оставь комментарий "
            'или нажми кнопку "Сохранить без комментария"',
            call.message.chat.id,
            message_id=call.message.id,
            reply_markup=keyboard,
        )
        await state.set(ReviewStates.write_comment)
        await state.add_data(value=rate_number)
