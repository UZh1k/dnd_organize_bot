from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from models import User
from utils.form.form_text_item import FormTextItem
from utils.handler.base_handler import BaseHandler


class RegistrationHandler(BaseHandler):
    form_items: list[FormTextItem] = []
    command: str

    async def first_step(
        self,
        message: Message,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        await self.form_items[0].prepare(message.chat.id, user, session, bot, state)

    async def last_step(
        self,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ): ...

    @classmethod
    def create_func_for_filter(cls, current_item):
        # trick to make functions with different prefixes
        prefix = current_item.gen_callback_root()

        def check(call):
            return call.data.startswith(prefix)

        return check

    def register_handlers(self):
        self.bot.register_message_handler(
            self.first_step,
            commands=[self.command],
            chat_types=["private"],
            pass_bot=True,
        )

        for step_i in range(len(self.form_items)):
            if step_i == len(self.form_items) - 1:
                next_step = self.last_step
            else:
                next_step = self.form_items[step_i + 1].prepare

            current_item = self.form_items[step_i](next_step)
            if current_item.with_message:
                self.bot.register_message_handler(
                    current_item.handle_message,
                    state=current_item.state,
                    content_types=["text"],
                    pass_bot=True,
                )
            if current_item.with_callback:
                self.bot.register_callback_query_handler(
                    current_item.handle_callback,
                    self.create_func_for_filter(current_item),
                    pass_bot=True,
                )
            if current_item.with_photo:
                self.bot.register_message_handler(
                    current_item.handle_photo,
                    state=current_item.state,
                    content_types=["photo"],
                    pass_bot=True,
                )
