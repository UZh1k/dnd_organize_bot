from abc import abstractmethod
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
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

    @abstractmethod
    async def handle_callback(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ): ...
