from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from controllers.game import GameController
from controllers.game_application import GameApplicationController
from controllers.review import ReviewController
from controllers.user import UserController
from handlers.game_application.invite import send_invite
from handlers.game_application.states import GameApplicationStates
from models import User, ReviewReceiverTypeEnum
from utils.message_helpers import (
    send_message_with_link_button,
    generate_link_for_game_apply,
    get_user_text,
    review_statistic_text,
    create_markup,
)

GAME_APPLICATION_CALLBACK_PREFIX = "GameApplication"
GAME_APPLICATION_NO_DATA = f"{GAME_APPLICATION_CALLBACK_PREFIX}:no_data"
GAME_APPLICATION_CANCEL = f"{GAME_APPLICATION_CALLBACK_PREFIX}:cancel"


class GameApplicationChoiceEnum(Enum):
    letter = "letter"
    no_data = "no_data"
    cancel = "cancel"


async def handle_apply_for_game(
    message: Message,
    bot: AsyncTeleBot,
    session: AsyncSession,
    user: User,
    state: StateContext,
):
    game_id = int(message.text.split()[-1])
    game = await GameController.get_one(game_id, session)
    if not game or not game.active:
        await bot.send_message(message.chat.id, "Игра уже неактивна")
        return
    if game.creator_id == user.id:
        await bot.send_message(
            message.chat.id, "Ты уже состоишь в игре, потому что ты ее создал."
        )
        return
    game_application = await GameApplicationController.get_one(
        game_id, user.id, session
    )
    if game_application:
        if not game_application.accepted:
            await bot.send_message(message.chat.id, "Ты уже подавал заявку на эту игру")
            return
        else:
            await send_invite(message.chat.id, bot, game)
            return
    if not user.registered:
        await send_message_with_link_button(
            bot,
            message.chat.id,
            f"Вижу, что тебя заинтересовала игра “{game.title}”. "
            "Зарегистрируйся при помощи команды /register, а затем опять подавайся",
            "Податься на игру",
            generate_link_for_game_apply(game),
        )
        return

    await state.set(GameApplicationStates.choice)
    await state.add_data(game_id=game_id)

    game_master = await UserController.get_one(game.creator_id, session)

    dm_statistic = await ReviewController.get_reviews_statistic(
        game.creator_id, session, ReviewReceiverTypeEnum.dm.value
    )
    review_text = review_statistic_text(dm_statistic)

    keyboard = [
        ("Написать сопроводительное сообщение", "letter"),
        ("Отправить заявку без сообщения", "no_data"),
        ("Отмена", "cancel"),
    ]
    if dm_statistic.total_count > 0:
        keyboard.insert(
            0,
            (
                "Посмотреть отзывы",
                f"reviews:{ReviewReceiverTypeEnum.dm.value}:{game.creator_id}",
            ),
        )

    markup = create_markup(keyboard, GAME_APPLICATION_CALLBACK_PREFIX)

    await bot.send_message(
        message.chat.id,
        f"Вижу, что тебя заинтересовала игра “{game.title}”. "
        f"Отправляю тебе анкету мастера этой игры.\n\n"
        f"{get_user_text(game_master)}\n\n"
        f"Оценка: {review_text}\n\n"
        f"Если тебя все устраивает, то я отправлю твою анкету мастеру. "
        f"Выбери одну из опций ниже.",
        reply_markup=markup,
    )
