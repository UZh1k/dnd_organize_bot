from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from models import User
from utils.form.form_text_item import FormTextItem


class FormChoiceTextItem(FormTextItem):
    with_callback = True
    row_width: int = 1
    form_name: str
    form_item_name: str

    alert_message: str
    choices: tuple[tuple[str, str], ...]

    @classmethod
    def gen_callback_root(cls):
        return f"{cls.form_name}:{cls.form_item_name}"

    @classmethod
    def gen_callback_data(cls, data: str):
        return f"{cls.gen_callback_root()}:{data}"

    @classmethod
    def prepare_markup(cls):
        markup = InlineKeyboardMarkup(row_width=cls.row_width)
        for name, data in cls.choices:
            markup.add(
                InlineKeyboardButton(name, callback_data=cls.gen_callback_data(data))
            )
        return markup

    async def handle_callback(
        self,
        call: CallbackQuery,
        bot: AsyncTeleBot,
        user: User,
        session: AsyncSession,
        state: StateContext,
    ):
        text = call.data.split(":")[-1]
        await self.save_answer(text, user, session)
        await bot.answer_callback_query(
            callback_query_id=call.id, text=self.alert_message
        )
        await bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id, reply_markup=None
        )
        await self.next_step(call.from_user.id, user, bot, state)
