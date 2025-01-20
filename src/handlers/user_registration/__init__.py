from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from src.consts import REGISTER_IMAGE
from src.handlers.user_registration.accept_minor import UserRegistrationAcceptMinor
from src.handlers.user_registration.age import UserRegistrationAge
from src.handlers.user_registration.bio import UserRegistrationBio
from src.handlers.user_registration.city import UserRegistrationCity
from src.handlers.user_registration.name import UserRegistrationName
from src.handlers.user_registration.timezone import UserRegistrationTimezone
from src.handlers.user_registration.user_type import UserRegistrationUserType
from src.models import User
from src.utils.form.form_item_group import FormItemGroup
from src.utils.handler_groups.registration_handler_group import RegistrationHandlerGroup


class UserRegistrationHandlerGroup(RegistrationHandlerGroup):
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
        if not user.registered:
            await bot.send_photo(
                message.chat.id,
                REGISTER_IMAGE,
                "Давай заполним с тобой короткую анкету. Данная анкета едина "
                "как для игроков, так и мастеров. Помни, что ты всегда можешь пройти "
                "регистрацию заново и изменить данные. Пожалуйста, не указывай фамилию, "
                "номер телефона и адрес проживания, мне не нужны твои персональные данные.",
            )
            await super().first_step(message, user, session, bot, state)
        else:
            await bot.send_message(
                message.chat.id,
                "Ты уже зарегистрирован. Если ты захочешь посмотреть свою "
                "анкету или скорректировать её, то выбери в меню слева внизу "
                "“Профиль” или отправь команду /profile.",
            )

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
            "Команда /create для создания игры, а команда /search для поиска.\n\n"
            "Если ты захочешь посмотреть свою анкету или скорректировать её, "
            "то выбери в меню слева внизу “Профиль” или отправь команду /profile.",
        )
