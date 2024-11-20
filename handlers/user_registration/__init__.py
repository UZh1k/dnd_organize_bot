from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from handlers.user_registration.age import UserRegistrationAge
from handlers.user_registration.bio import UserRegistrationBio
from handlers.user_registration.city import UserRegistrationCity
from handlers.user_registration.name import UserRegistrationName
from handlers.user_registration.timezone import UserRegistrationTimezone
from handlers.user_registration.user_type import UserRegistrationUserType
from models import User
from utils.form.form_text_item import FormTextItem
from utils.handler.base_handler import BaseHandler


class UserRegistrationHandler(BaseHandler):
    form_items: list[FormTextItem] = [
        UserRegistrationName,
        UserRegistrationAge,
        UserRegistrationCity,
        UserRegistrationTimezone,
        UserRegistrationUserType,
        UserRegistrationBio,
    ]
    command: str = "register"

    async def first_step(
        self, message: Message, user: User, bot: AsyncTeleBot, state: StateContext
    ):
        await self.form_items[0].prepare(message.chat.id, user, bot, state)

    async def last_step(
        self, chat_id: int, user: User, bot: AsyncTeleBot, state: StateContext
    ):
        user.registered = True
        await state.delete()
        await bot.send_message(
            chat_id, "Регистрация прошла успешно, теперь открыты все функции"
        )

    @classmethod
    def create_func_for_filter(cls, current_item):
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
                    pass_bot=True,
                )
            if current_item.with_callback:
                # prefix = current_item.gen_callback_root()
                self.bot.register_callback_query_handler(
                    current_item.handle_callback,
                    self.create_func_for_filter(current_item),
                    pass_bot=True,
                )
