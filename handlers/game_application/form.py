from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio import StateContext
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from controllers.game import GameController
from controllers.game_application import GameApplicationController
from controllers.user import UserController
from handlers.game_application.invite import send_invite
from handlers.game_application.states import GameApplicationStates
from models import User
from utils.message_helpers import (
    send_message_with_link_button,
    generate_link_for_game_apply,
    get_user_text,
)

GAME_APPLICATION_CALLBACK_PREFIX = "GameApplication"
GAME_APPLICATION_NO_DATA = f"{GAME_APPLICATION_CALLBACK_PREFIX}:no_data"
GAME_APPLICATION_CANCEL = f"{GAME_APPLICATION_CALLBACK_PREFIX}:cancel"


class GameApplicationChoiceEnum(Enum):
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
    await state.set(GameApplicationStates.letter)
    await state.add_data(game_id=game_id)
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "Отправить без сообщения", callback_data=GAME_APPLICATION_NO_DATA
        ),
        InlineKeyboardButton("Отмена", callback_data=GAME_APPLICATION_CANCEL),
    )

    game_master = await UserController.get_one(game.creator_id, session)
    await bot.send_message(
        message.chat.id,
        f"Вижу, что тебя заинтересовала игра “{game.title}”. "
        f"Отправляю тебе анкету мастера этой игры.\n\n"
        f"{get_user_text(game_master)}\n\n"
        f"Если тебя все устраивает, то я отправлю твою анкету мастеру. "
        f"Если хочешь приложить к анкете сопроводительное сообщение, например, "
        f"ты уже знаешь за кого и какой класс хочешь играть, то отправь в "
        f"ответ текстовое сообщение вместо нажатия кнопок.",
        reply_markup=markup,
    )
