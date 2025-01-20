from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from src.consts import CREATE_IMAGE
from src.controllers.game import GameController
from src.controllers.game_tag_link import GameTagLinkController
from src.handlers.game_registration.about_price import GameRegistrationAboutPrice
from src.handlers.game_registration.accept_city import GameRegistrationAcceptCity
from src.handlers.game_registration.accept_offline import GameRegistrationAcceptOffline
from src.handlers.game_registration.city import GameRegistrationCity
from src.handlers.game_registration.description import GameRegistrationDescription
from src.handlers.game_registration.dnd_redaction import GameRegistrationDndRedaction
from src.handlers.game_registration.dnd_setting import GameRegistrationDndSetting
from src.handlers.game_registration.format import GameRegistrationFormat
from src.handlers.game_registration.free import GameRegistrationFree
from src.handlers.game_registration.game_time import GameRegistrationTime
from src.handlers.game_registration.game_type import GameRegistrationType
from src.handlers.game_registration.image import GameRegistrationImage
from src.handlers.game_registration.players_age import GameRegistrationPlayersAge
from src.handlers.game_registration.players_count import GameRegistrationPlayersCount
from src.handlers.game_registration.redaction_and_setting import (
    GameRegistrationRedactionAndSetting,
)
from src.handlers.game_registration.start_level import GameRegistrationStartLevel
from src.handlers.game_registration.system import GameRegistrationSystem
from src.handlers.game_registration.tag import GameRegistrationTag
from src.handlers.game_registration.tech_requirements import (
    GameRegistrationTechRequirements,
)
from src.handlers.game_registration.title import GameRegistrationTitle
from src.models import User
from src.utils.form.form_item_group import FormItemGroup
from src.utils.handler_groups.registration_handler_group import RegistrationHandlerGroup


class GameRegistrationHandlerGroup(RegistrationHandlerGroup):
    form_item_groups: tuple[FormItemGroup] = (
        FormItemGroup(main=GameRegistrationTitle),
        FormItemGroup(
            main=GameRegistrationFormat,
            side=(
                GameRegistrationAcceptOffline,
                GameRegistrationAcceptCity,
                GameRegistrationCity,
            ),
        ),
        FormItemGroup(main=GameRegistrationPlayersCount),
        FormItemGroup(main=GameRegistrationFree, side=(GameRegistrationAboutPrice,)),
        FormItemGroup(main=GameRegistrationTime),
        FormItemGroup(main=GameRegistrationType),
        FormItemGroup(
            main=GameRegistrationSystem,
            side=(
                GameRegistrationDndRedaction,
                GameRegistrationDndSetting,
                GameRegistrationRedactionAndSetting,
            ),
        ),
        FormItemGroup(main=GameRegistrationDescription),
        FormItemGroup(main=GameRegistrationStartLevel),
        FormItemGroup(main=GameRegistrationPlayersAge),
        FormItemGroup(main=GameRegistrationTechRequirements),
        FormItemGroup(main=GameRegistrationImage),
        FormItemGroup(main=GameRegistrationTag),
    )
    command: str = "create"
    form_prefix: str = "GameRegistration"

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
                message.chat.id,
                "Не узнаю тебя. Ты точно зарегистрировался? Нажми /register",
            )
            return
        await bot.send_photo(
            message.chat.id,
            CREATE_IMAGE,
            "А теперь к приключениям! Ответь на мои вопросы и "
            "я смогу опубликовать твою игру.\n\n"
            "Обрати внимание, что все публикации с рекламой, фотографиями людей, "
            "нецензурными или излишне жестокими картинками, политическими или "
            "религиозными высказываниями, пропагандой наркотиков, разжиганием "
            "национальной и прочей вражды, матами, информацией не по теме поиска "
            "игроков будут удалены. Нарушение приведет к перманентному бану.",
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
        async with state.data() as data:
            data["creator_id"] = user.id
            tags = data.pop("tags", [])

        game = await GameController.create(data, session)
        for tag_id in tags:
            await GameTagLinkController.create(
                {"tag_id": tag_id, "game_id": game.id}, session
            )

        await state.delete()
        await bot.send_message(
            chat_id,
            "Твоя игра успешно сохранена. "
            "Для публикации осталось пройти пару шагов.\n\n"
            "Тебе нужно создать новую группу в Телеграмм, в которой ты будешь "
            "собирать игроков и обсуждать предстоящую игру. А я смогу пригласить "
            "в нее игроков. Для этого, после создания группы, добавь меня - "
            "@sneakydicebot. В группе ты получишь от меня информацию, "
            "как начать подбор.",
        )