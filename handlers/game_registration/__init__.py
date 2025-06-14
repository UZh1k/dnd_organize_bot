from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message

from consts import CREATE_IMAGE
from controllers.game import GameController
from controllers.game_tag_link import GameTagLinkController
from handlers.game_registration.about_price import GameRegistrationAboutPrice
from handlers.game_registration.accept_city import GameRegistrationAcceptCity
from handlers.game_registration.accept_offline import GameRegistrationAcceptOffline
from handlers.game_registration.city import GameRegistrationCity
from handlers.game_registration.description import GameRegistrationDescription
from handlers.game_registration.dnd_redaction import GameRegistrationDndRedaction
from handlers.game_registration.dnd_setting import GameRegistrationDndSetting
from handlers.game_registration.format import GameRegistrationFormat
from handlers.game_registration.free import GameRegistrationFree
from handlers.game_registration.game_time import GameRegistrationTime
from handlers.game_registration.game_type import GameRegistrationType
from handlers.game_registration.image import GameRegistrationImage
from handlers.game_registration.players_age import GameRegistrationPlayersAge
from handlers.game_registration.players_count import GameRegistrationPlayersCount
from handlers.game_registration.redaction_and_setting import (
    GameRegistrationRedactionAndSetting,
)
from handlers.game_registration.start_level import GameRegistrationStartLevel
from handlers.game_registration.system import GameRegistrationSystem
from handlers.game_registration.tag import GameRegistrationTag
from handlers.game_registration.tech_requirements import (
    GameRegistrationTechRequirements,
)
from handlers.game_registration.title import GameRegistrationTitle
from models import User
from utils.form.form_item_group import FormItemGroup
from utils.handler_groups.registration_handler_group import RegistrationHandlerGroup


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
        **kwargs,
    ):
        async with state.data() as data:
            data["creator_id"] = user.id
            tags = data.pop("tags", [])

        data["create_datetime"] = datetime.now()
        game = await GameController.create(data, session)
        for tag_id in tags:
            await GameTagLinkController.create(
                {"tag_id": tag_id, "game_id": game.id}, session
            )

        await state.delete()
        await bot.send_message(
            chat_id,
            "Твоя игра успешно сохранена, но она еще не в канале.\n\n"
            "❗️❗️❗️\n"
            "Для публикации осталось пройти пару шагов. "
            "Тебе нужно создать новую группу в Телеграмм, не канал, "
            "а именно группу, в которой ты будешь собирать игроков и "
            "обсуждать предстоящую игру. А я смогу пригласить в эту группу "
            "игроков. Для этого, после создания группы, добавь меня - "
            "@sneakydicebot. В группе ты получишь от меня информацию, "
            "как начать подбор.\n\n"
            " Если ты захочешь скорректировать "
            "публикацию, то воспользуйся командой редактирование в меню слева "
            "внизу или отправь /edit.\n\n",
        )
