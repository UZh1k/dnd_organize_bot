from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from consts import REGISTER_IMAGE
from handlers.user_registration.accept_minor import UserRegistrationAcceptMinor
from handlers.user_registration.age import UserRegistrationAge
from handlers.user_registration.bio import UserRegistrationBio
from handlers.user_registration.city import UserRegistrationCity
from handlers.user_registration.name import UserRegistrationName
from handlers.user_registration.timezone import UserRegistrationTimezone
from handlers.user_registration.user_type import UserRegistrationUserType
from models import User
from utils.form.form_item_group import FormItemGroup
from utils.handler.registration_handler_group import RegistrationHandlerGroup


class UserRegistrationHandler(RegistrationHandlerGroup):
    form_item_groups: tuple[FormItemGroup] = (
        FormItemGroup(main=UserRegistrationName),
        FormItemGroup(main=UserRegistrationAge, side=(UserRegistrationAcceptMinor,)),
        FormItemGroup(main=UserRegistrationCity, side=(UserRegistrationTimezone,)),
        FormItemGroup(main=UserRegistrationUserType),
        FormItemGroup(main=UserRegistrationBio),
    )
    command: str = "register"
    form_prefix: str = "UserRegistration"

    async def first_step(
        self,
        message: Message,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        await bot.send_photo(
            message.chat.id,
            REGISTER_IMAGE,
            "Давай заполним с тобой короткую анкету. Данная анкета едина "
            "как для игроков, так и мастеров. Помни, что ты всегда можешь пройти "
            "регистрацию заново и изменить данные. Пожалуйста, не указывай фамилию, "
            "номер телефона и адрес проживания, мне не нужны твои персональные данные.",
        )
        await super().first_step(message, user, session, bot, state)

    async def last_step(
        self,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
        form_prefix: str,
    ):
        user.registered = True
        await state.delete()
        await bot.send_message(
            chat_id,
            "Поздравляю! Теперь мы можем с тобой найти или создать игру. "
            "Открой меню слева внизу, чтобы выбрать, с чем я могу тебе помочь. "
            "Команда /create для создания игры, а команда /search для поиска.",
        )
