from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from models import User
from utils.form.form_choice_text_item import FormChoiceTextItem
from utils.form.form_item_group import FormItemGroup
from utils.handler_groups.base_handler_group import BaseHandlerGroup
from utils.other import is_command


class RegistrationHandlerGroup(BaseHandlerGroup):
    form_item_groups: tuple[FormItemGroup] = []
    command: str
    form_prefix: str

    async def first_step(
        self,
        message: Message,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        await self.form_item_groups[0].main.prepare(
            message.chat.id, user, session, bot, state, self.form_prefix
        )

    async def last_step(
        self,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        form_prefix: str,
    ): ...

    @classmethod
    def create_func_for_filter(cls, current_item: FormChoiceTextItem):
        # trick to make functions with different prefixes
        prefix = current_item.gen_callback_root(cls.form_prefix)

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

        for step_i in range(len(self.form_item_groups)):
            if step_i == len(self.form_item_groups) - 1:
                next_step = self.last_step
            else:
                next_step = self.form_item_groups[step_i + 1].main.prepare

            current_item_group = self.form_item_groups[step_i]
            for current_item in (current_item_group.main, *current_item_group.side):
                current_item_obj = current_item(next_step, self.form_prefix)
                if current_item_obj.with_message:
                    self.bot.register_message_handler(
                        current_item_obj.handle_message,
                        func=lambda message: not is_command(message.text),
                        state=current_item_obj.state,
                        content_types=["text"],
                        pass_bot=True,
                    )
                if current_item_obj.with_callback:
                    self.bot.register_callback_query_handler(
                        current_item_obj.handle_callback,
                        self.create_func_for_filter(current_item_obj),
                        pass_bot=True,
                    )
                if current_item_obj.with_photo:
                    self.bot.register_message_handler(
                        current_item_obj.handle_photo,
                        state=current_item_obj.state,
                        content_types=["photo", "document"],
                        pass_bot=True,
                    )
