from abc import ABC
from typing import Callable, Awaitable

from sqlalchemy.ext.asyncio import AsyncSession
from telebot import State
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message, CallbackQuery

from models import User
from utils.other import contains_link


class FormTextItem(ABC):
    state: State
    prepare_text: str
    message_length: int | None = 100

    with_message: bool = True
    with_callback: bool = False
    with_photo: bool = False

    def __init__(self, next_step: Callable[..., Awaitable], form_prefix: str):
        self.next_step = next_step
        self.form_prefix = form_prefix

    @classmethod
    async def prepare_markup(
        cls, form_prefix: str, session: AsyncSession, state: StateContext, **kwargs
    ):
        return None

    @classmethod
    async def prepare(
        cls,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        form_prefix: str,
        **kwargs,
    ):
        await state.set(cls.state)
        await bot.send_message(
            chat_id,
            cls.prepare_text.format(user=user),
            reply_markup=await cls.prepare_markup(
                form_prefix, session, state, user=user, **kwargs
            ),
        )

    @classmethod
    async def check_message_length(
        cls, message: Message, bot: AsyncTeleBot, message_length: int = 100
    ):
        if message.text and len(message.text) > message_length:
            await bot.send_message(
                message.chat.id,
                "Мне кажется, что твое сообщение слишком длинное. "
                f"Пожалуйста, постарайся уместиться в {message_length} символов.\n\n"
                f"Это обусловлено ограничениями самого мессенджера, "
                f"посты не могут превышать определенной длины.",
            )
            return False
        return True

    @classmethod
    async def check_has_no_links(cls, message: Message, bot: AsyncTeleBot):
        if contains_link(message.text):
            await bot.send_message(
                message.chat.id,
                "Похоже, что текст содержит ссылку. Пожалуйста, перепиши без нее.",
            )
            return False
        return True

    @classmethod
    async def check_has_no_bad_symbols(cls, message: Message, bot: AsyncTeleBot):
        if "*" in message.text or "_" in message.text or "#" in message.text:
            await bot.send_message(
                message.chat.id,
                "Похоже, что текст содержит один из символов: “*”, “#” или “_”. "
                "Пожалуйста, перепиши без них.",
            )
            return False
        return True

    @classmethod
    async def check_is_not_digit(cls, message: Message, bot: AsyncTeleBot) -> bool:
        if message.text.isdigit():
            await bot.send_message(
                message.chat.id,
                "Не смог разобрать твой ответ, пожалуйста, "
                "попробуй написать по-другому",
            )
            return False
        return True

    async def validate_answer(self, message: Message, bot: AsyncTeleBot) -> bool:
        if await self.check_has_no_links(
            message, bot
        ) and await self.check_has_no_bad_symbols(message, bot):
            if self.message_length:
                return await self.check_message_length(
                    message, bot, message_length=self.message_length
                )
        return False

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
        **kwargs,
    ):
        await self.next_step(
            chat_id, user, session, bot, state, self.form_prefix, **kwargs
        )

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
