from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.states.asyncio import StateContext
from telebot.types import CallbackQuery

from src.models import User
from src.utils.handlers.base_handler import BaseHandler, FunctionType


class BaseMessageHandler(BaseHandler, ABC):
    type = FunctionType.message

    async def handle_callback(
        self,
        call: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: StateContext,
    ):
        pass
