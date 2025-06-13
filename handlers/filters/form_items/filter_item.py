from abc import abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import InlineKeyboardButton

from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem


class FilterItem(FormChoiceTextItem):
    clean_callback = "clean"
    set_field: str

    @classmethod
    async def prepare_answer(
        cls, name: str, set_filters: dict[str, Any], session: AsyncSession
    ) -> str:
        return name

    @abstractmethod
    async def on_clean(self, state: StateContext): ...

    async def save_answer(
        self, text: str, user: User, session: AsyncSession, state: StateContext
    ):
        if text == self.clean_callback:
            await self.on_clean(state)
            return

        await super().save_answer(text, user, session, state)

    @classmethod
    async def prepare_markup(
        cls, form_prefix: str, session: AsyncSession, state: StateContext, **kwargs
    ):
        markup = await super().prepare_markup(form_prefix, session, state, **kwargs)

        data_is_set = False
        async with state.data() as data:
            data_is_set = data.get(cls.set_field) is not None

        if data_is_set:
            markup.add(
                InlineKeyboardButton(
                    "Очистить",
                    callback_data=cls.gen_callback_data(
                        cls.clean_callback, form_prefix
                    ),
                )
            )
        return markup

    @classmethod
    async def prepare(
        cls,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        form_prefix: str,
        edit_message_id: int = None,
        **kwargs,
    ):
        await state.set(cls.state)
        text = cls.prepare_text.format(user=user)
        markup = await cls.prepare_markup(form_prefix, session, state, **kwargs)
        if edit_message_id:
            await bot.edit_message_text(
                text,
                chat_id,
                message_id=edit_message_id,
                reply_markup=markup,
            )
        else:
            await bot.send_message(
                chat_id,
                text,
                reply_markup=markup,
            )
