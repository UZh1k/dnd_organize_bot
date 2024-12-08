from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from consts import CREATE_IMAGE
from controllers.game import GameController
from handlers.game_registration.about_price import GameRegistrationAboutPrice
from handlers.game_registration.accept_offline import GameRegistrationAcceptOffline
from handlers.game_registration.city import GameRegistrationCity
from handlers.game_registration.description import GameRegistrationDescription
from handlers.game_registration.format import GameRegistrationFormat
from handlers.game_registration.free import GameRegistrationFree
from handlers.game_registration.game_time import GameRegistrationTime
from handlers.game_registration.game_type import GameRegistrationType
from handlers.game_registration.image import GameRegistrationImage
from handlers.game_registration.players_age import GameRegistrationPlayersAge
from handlers.game_registration.players_count import GameRegistrationPlayersCount
from handlers.game_registration.system import GameRegistrationSystem
from handlers.game_registration.tech_requirements import (
    GameRegistrationTechRequirements,
)
from handlers.game_registration.title import GameRegistrationTitle
from models import User
from utils.form import RegistrationHandler, FormTextItem


class GameRegistrationHandler(RegistrationHandler):
    form_items: list[FormTextItem] = [
        GameRegistrationTitle,
        GameRegistrationFormat,
        GameRegistrationAcceptOffline,
        GameRegistrationCity,
        GameRegistrationPlayersCount,
        GameRegistrationFree,
        GameRegistrationAboutPrice,
        GameRegistrationTime,
        GameRegistrationType,
        GameRegistrationSystem,
        GameRegistrationDescription,
        GameRegistrationPlayersAge,
        GameRegistrationTechRequirements,
        GameRegistrationImage,
    ]
    command: str = "create"

    async def first_step(
        self,
        message: Message,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        if not user.registered:
            await bot.send_message(
                message.chat.id,
                "Не узнаю тебя. Ты точно зарегистрировался? Нажми /register",
            )
            return
        await bot.send_photo(
            message.chat.id,
            CREATE_IMAGE,
            "Ура! Время приключений! "
            "Ответь на мои вопросы и я смогу опубликовать твою игру.",
        )
        await super().first_step(message, user, session, bot, state)

    async def last_step(
        self,
        chat_id: int,
        user: User,
        session: AsyncSession,
        bot: AsyncTeleBot,
        state: StateContext,
    ):
        async with state.data() as data:
            data["creator_id"] = user.id
            await GameController.create(data, session)
        await bot.send_message(
            chat_id,
            "Твоя игра успешно сохранена. "
            "Для публикации осталось пройти пару шагов.\n\n"
            "Создай группу в Телеграмм. Добавь меня в группу. "
            "Меня зовут @sneakydicebot. После этого дай мне права администратора. "
            "В группе ты получишь от меня сообщения с информацией по привязке.",
        )
