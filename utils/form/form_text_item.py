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
    with_photo: bool = False

    def __init__(self, next_step: Callable[..., Awaitable]):
        self.next_step = next_step

    @classmethod
    def prepare_markup(cls):
        return None

    @classmethod
    async def prepare(
        cls,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        await state.set(cls.state)
        await bot.send_message(
            chat_id, cls.prepare_text, reply_markup=cls.prepare_markup()
        )

    @classmethod
    async def check_message_length(
        cls, message: Message, bot: AsyncTeleBot, message_length: int = 100
    ):
        if message.text and len(message.text) > message_length:
            await bot.send_message(
                message.chat.id,
                "Мне кажется, что твое сообщение слишком длинное. "
                f"Пожалуйста, постарайся уместиться в {message_length} символов.",
            )
            return False
        return True

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        return True

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ): ...

    async def on_answered(
        self,
        answer: str,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        await self.next_step(chat_id, user, session, bot, state)

    async def handle_message(
        self,
        message: Message,
        bot: AsyncTeleBot,
        user: User,
        session: AsyncSession,
        state: StateContext,
    ):
        if await self.validate_answer(message, bot):
            await self.save_answer(message.text, user, session, state)
            await self.on_answered(
                message.text, message.chat.id, user, session, bot, state
            )

    async def handle_photo(
        self,
        message: Message,
        bot: AsyncTeleBot,
        user: User,
        session: AsyncSession,
        state: StateContext,
    ): ...

    async def handle_callback(
        self,
        call: CallbackQuery,
        bot: AsyncTeleBot,
        user: User,
        session: AsyncSession,
        state: StateContext,
    ): ...
