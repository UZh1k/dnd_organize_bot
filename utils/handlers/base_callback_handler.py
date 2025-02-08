from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import Message, CallbackQuery

from models import User
from utils.handlers.base_handler import BaseHandler, FunctionType


class BaseCallbackHandler(BaseHandler, ABC):
    type = FunctionType.callback

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        pass

    async def check_callback_not_processed(self, call: CallbackQuery) -> bool:
        try:
            await self.bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=None
            )
            return True
        except ApiTelegramException:
            return False

    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        ...

    async def handle_callback(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        if await self.check_callback_not_processed(call):
            await self.on_action(call, session, user, state)
