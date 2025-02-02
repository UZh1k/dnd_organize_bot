from enum import Enum
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from telebot.states.asyncio import StateContext
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from controllers.game import GameController
from controllers.game_application import GameApplicationController
from handlers.game_application.invite import send_invite
from models import User

ACCEPT_FORM_CALLBACK_PREFIX = "AcceptForm"

from telebot.async_telebot import AsyncTeleBot

class ApplyAnswer(Enum):
    yes = "yes"
    no = "no"


def generate_accept_callback(game_id: int, user_id: int, answer: Literal["yes", "no"]):
    return f"{ACCEPT_FORM_CALLBACK_PREFIX}:{game_id}:{user_id}:{answer}"


def get_data_from_accept_callback(callback_data: str) -> tuple[int, int]:
    _, game_id, user_id, _ = callback_data.split(":")
    return int(game_id), int(user_id)


def generate_accept_form_markup(game_id: int, user_id: int):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(
            "Одобрить",
            callback_data=generate_accept_callback(
                game_id, user_id, ApplyAnswer.yes.value
            ),
        ),
        InlineKeyboardButton(
            "Отклонить",
            callback_data=generate_accept_callback(
                game_id, user_id, ApplyAnswer.no.value
            ),
        ),
    )
    return markup


async def handle_decline_application(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    session: AsyncSession,
    user: User,
    state: StateContext,
):
    try:
        await bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id, reply_markup=None
        )
    except ApiTelegramException:
        return
    game_id, user_id = get_data_from_accept_callback(call.data)
    game = await GameController.get_one(game_id, session)
    await GameApplicationController.set_status(game_id, user_id, False, session)
    await bot.send_message(
        user_id,
        f"К сожалению, мастер игры “{game.title}” не принял твою анкету или "
        f"сбор на игру уже был закрыт. Не отчаивайся, посмотри еще игры - "
        f"https://t.me/SneakyDiceGames.",
    )
    # await bot.answer_callback_query(callback_query_id=call.id, text="Отправил отказ")
    await bot.send_message(call.message.chat.id, "Отправил отказ")


async def handle_accept_application(
    call: CallbackQuery,
    bot: AsyncTeleBot,
    session: AsyncSession,
    user: User,
    state: StateContext,
):
    try:
        await bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id, reply_markup=None
        )
    except ApiTelegramException:
        return
    game_id, user_id = get_data_from_accept_callback(call.data)
    game = await GameController.get_one(game_id, session)
    await GameApplicationController.set_status(game_id, user_id, True, session)

    await send_invite(user_id, bot, game)

    # await bot.answer_callback_query(
    #     callback_query_id=call.id, text="Отправил приглашение"
    # )
    await bot.send_message(call.message.chat.id, "Отправил приглашение")
