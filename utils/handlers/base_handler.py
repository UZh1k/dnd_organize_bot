from abc import abstractmethod
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import Message, CallbackQuery

from models import User


class FunctionType(Enum):
    message = "message"
    callback = "callback"


class BaseHandler:
    type: FunctionType

    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    @abstractmethod
    def register_handler(self): ...

    @abstractmethod
    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ): ...

    async def check_callback_not_processed(self, call: CallbackQuery) -> bool:
        try:
            await self.bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=None
            )
            return True
        except ApiTelegramException:
            return False

    @abstractmethod
    async def on_action(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ): ...

    async def handle_callback(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        if await self.check_callback_not_processed(call):
            await self.on_action(call, session, user, state)
