from abc import ABC
from typing import Callable, Awaitable

from sqlalchemy.ext.asyncio import AsyncSession
from telebot import State
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message, CallbackQuery

from models import User


class FormTextItem(ABC):
    state: State
    prepare_text: str

    with_message: bool = True
    with_callback: bool = False

    def __init__(self, next_step: Callable[..., Awaitable]):
        self.next_step = next_step

    @classmethod
    def prepare_markup(cls):
        return None

    @classmethod
    async def prepare(
        cls, chat_id: int, user: User, bot: AsyncTeleBot, state: StateContext
    ):
        await state.set(cls.state)
        await bot.send_message(
            chat_id, cls.prepare_text, reply_markup=cls.prepare_markup()
        )

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        return True

    async def save_answer(self, text: str, user: User, session: AsyncSession): ...

    async def handle_message(
        self,
        message: Message,
        bot: AsyncTeleBot,
        user: User,
        session: AsyncSession,
        state: StateContext,
    ):
        if await self.validate_answer(message, bot):
            await self.save_answer(message.text, user, session)
            await self.next_step(message.chat.id, user, bot, state)

    async def handle_callback(
        self,
        call: CallbackQuery,
        bot: AsyncTeleBot,
        user: User,
        session: AsyncSession,
        state: StateContext,
    ): ...
