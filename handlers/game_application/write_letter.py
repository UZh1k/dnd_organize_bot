from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from handlers.game_application import GameApplicationStates
from handlers.game_application.form import GAME_APPLICATION_CALLBACK_PREFIX
from models import User
from utils.handlers.base_callback_handler import BaseCallbackHandler
from utils.message_helpers import create_markup


class ApplicationWriteLetterHandler(BaseCallbackHandler):
    def register_handler(self):
        self.bot.register_callback_query_handler(
            self.handle_callback,
            func=lambda call: (
                call.data.startswith(f"{GAME_APPLICATION_CALLBACK_PREFIX}:letter")
            ),
        )

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        markup = create_markup(
            (
                ("Отправить заявку без сообщения", "no_data"),
                ("Отмена", "cancel"),
            ),
            GAME_APPLICATION_CALLBACK_PREFIX,
        )

        await state.set(GameApplicationStates.letter)

        await self.bot.send_message(
            call.message.chat.id,
            "Напиши сообщение, которое я отправлю мастеру вместе с твоей заявкой.",
            reply_markup=markup,
        )
