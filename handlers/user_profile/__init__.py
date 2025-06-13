from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import Message, CallbackQuery

from handlers.user_profile.accept_minor import UserProfileAcceptMinor
from handlers.user_profile.age import UserProfileAge
from handlers.user_profile.bio import UserProfileBio
from handlers.user_profile.city import UserProfileCity
from handlers.user_profile.name import UserProfileName
from handlers.user_profile.profile import handle_get_profile
from handlers.user_profile.timezone import UserProfileTimezone
from handlers.user_profile.user_type import UserProfileUserType
from models import User
from utils.form.form_item_group import FormItemGroup
from utils.handler_groups.registration_handler_group import RegistrationHandlerGroup
from utils.message_helpers import get_user_text


class UserProfileHandlerGroup(RegistrationHandlerGroup):
    form_item_groups: tuple[FormItemGroup] = (
        FormItemGroup(main=UserProfileName),
        FormItemGroup(main=UserProfileAge, side=(UserProfileAcceptMinor,)),
        FormItemGroup(main=UserProfileCity, side=(UserProfileTimezone,)),
        FormItemGroup(main=UserProfileUserType),
        FormItemGroup(main=UserProfileBio),
    )
    command: str = "profile"
    form_prefix: str = "UserProfile"

    form_item_name_accept_edit: str = "accept_edit"
    form_item_name_edit_options: str = "edit_options"

    edit_option_handler_map = {
        "name": UserProfileName,
        "age": UserProfileAge,
        "city": UserProfileCity,
        "timezone": UserProfileTimezone,
        "user_type": UserProfileUserType,
        "bio": UserProfileBio,
    }

    async def first_step(
        self,
        message: Message,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        await state.delete()
        if not user.registered:
            await bot.send_message(
                message.chat.id, "Не узнаю тебя. Ты точно зарегистрировался?"
            )
        else:
            markup = self.create_markup(
                (("Редактировать", "yes"), ("Все ОК", "no")),
                self.form_item_name_accept_edit,
                row_width=2,
            )
            await bot.send_message(
                message.chat.id,
                f"Вот твоя анкета. Если хочешь её скорректировать, "
                f"то нажми на кнопку.\n\n"
                f"{get_user_text(user)}",
                reply_markup=markup,
            )

    async def last_step(
        self,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        form_prefix: str,
        **kwargs,
    ):
        await state.delete()
        markup = self.create_markup(
            (("Редактировать", "yes"), ("Все ОК", "no")),
            self.form_item_name_accept_edit,
            row_width=2,
        )
        await bot.send_message(
            chat_id,
            f"Анкета успешно обновлена.\n\n" f"{get_user_text(user)}",
            reply_markup=markup,
        )

    async def handle_skip_edit(
        self,
        call: CallbackQuery,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        try:
            await bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=None
            )
        except ApiTelegramException:
            pass

    async def handle_edit(
        self,
        call: CallbackQuery,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        try:
            await bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=None
            )
        except ApiTelegramException:
            return
        edit_options = (
            ("Имя", "name"),
            ("Возраст", "age"),
            ("Город", "city"),
            ("Часовой пояс", "timezone"),
            ("Роль в НРИ", "user_type"),
            ("Об игроке", "bio"),
            ("Всё ОК", "no"),
        )
        markup = self.create_markup(
            edit_options,
            self.form_item_name_edit_options,
        )
        await bot.send_message(
            call.message.chat.id,
            "Выбери, что ты хочешь скорректировать",
            reply_markup=markup,
        )

    async def prepare_form_item(
        self,
        call: CallbackQuery,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        try:
            await bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=None
            )
        except ApiTelegramException:
            return
        edit_option = call.data.split(":")[-1]
        await self.edit_option_handler_map[edit_option].prepare(
            call.message.chat.id,
            user,
            session,
            bot,
            state,
            self.form_prefix,
        )

    def register_handlers(self):
        self.bot.register_message_handler(
            self.first_step,
            chat_types=["private"],
            commands=["profile"],
            pass_bot=True,
        )
        self.bot.register_callback_query_handler(
            self.handle_skip_edit,
            func=lambda call: (
                call.data
                in (
                    f"{self.form_prefix}:{self.form_item_name_accept_edit}:no",
                    f"{self.form_prefix}:{self.form_item_name_edit_options}:no",
                )
            ),
            pass_bot=True,
        )
        self.bot.register_callback_query_handler(
            self.handle_edit,
            func=lambda call: (
                call.data == f"{self.form_prefix}:{self.form_item_name_accept_edit}:yes"
            ),
            pass_bot=True,
        )
        self.bot.register_callback_query_handler(
            self.prepare_form_item,
            func=lambda call: (
                call.data.startswith(
                    f"{self.form_prefix}:{self.form_item_name_edit_options}"
                )
            ),
            pass_bot=True,
        )

        for current_item_group in self.form_item_groups:

            for current_item in (current_item_group.main, *current_item_group.side):
                self.register_form_handlers(
                    current_item(self.last_step, self.form_prefix)
                )
