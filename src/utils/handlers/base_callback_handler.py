from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import Message

from src.models import User
from src.utils.handlers.base_handler import BaseHandler, FunctionType


class BaseCallbackHandler(BaseHandler, ABC):
    type = FunctionType.callback

    async def handle_message(
        self, message: Message, session: AsyncSession, user: User, state: StateContext
    ):
        pass
